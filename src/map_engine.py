"""
Implementation of class to perform mass operations on imap account
"""

from hashlib import sha1
import imaplib
import json
import logging
from pathlib import Path
import re

from .mail_config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

# pylint: disable=logging-fstring-interpolation


def sha1_data(data):
    """Calculate sha1 hash of data."""
    return sha1(data).hexdigest()


class MapEngine:
    """
    Class for mass operations on imap accounts
    """
    PATTERN_UID = re.compile(r'''\d+ \(UID (?P<uid>\d+)\)''')

    def __init__(self):
        """
        Constructor
        """
        settings = config()
        host, username, password = (
            settings[key]
            for key in ('EMAIL_HOST', 'EMAIL_USERNAME', 'EMAIL_PASSWORD')
        )

        logger.info(f"imap = imaplib.IMAP4_SSL('{host}')")
        self.imap = imaplib.IMAP4_SSL(host)

        logger.info(f"imap.login('{username}')")
        self.imap.login(username, password)

        self.imap.Debug = 4
        settings = None
        host, username, password = None, None, None

    def __enter__(self):
        """
        __enter__ method for context manager
        """
        return self

    def __exit__(self, _type, value, traceback):
        """
        __exit__ method for context manager
        """
        try:
            logger.info("imap.close()")
            self.imap.close()
        except Exception as err:
            logger.error(err)
        try:
            logger.info("imap.logout()")
            self.imap.logout()
        except Exception as err:
            logger.error(err)

    def apply(self, filename: Path):
        """
        Apply a file of commands to the account
        """
        op_map = {
            "move": self.move,
            "delete": self.delete,
            "download": self.download,
        }
        try:
            data: str = filename.read_text()
            objs = json.loads(data)
        except Exception as exc:  # pylint: disable=broad-except
            print(exc)
        else:
            for obj in objs:
                optype = obj.pop("optype")
                try:
                    op_map[optype](**obj)
                except KeyError as err:
                    print(err)

    def download(self, src_folder: str, dst_dir_name: str):
        """
        Move messages from email address from_addr
        from src_folder to dst_folder
        """
        print(f"Download folder {src_folder} to directory {dst_dir_name}")
        dst_directory: Path = Path(dst_dir_name).expanduser()

        email_ids = self._matching_folder(self.imap, src_folder)
        logger.info(f"Downloading {len(email_ids)} emails")

        for email_id in email_ids:
            logger.info(f"imap.fetch(str('{email_id}'), '(RFC822)')")
            _, data = self.imap.fetch(str(email_id), "(RFC822)")

            message = data[0][1]
            email_sha1: str = sha1_data(message)

            email_filename: str = f"{email_sha1}.txt"
            print(f"\tDownloading {email_id} {email_filename}")
            fullpath: Path = dst_directory.joinpath(email_filename)
            if not fullpath.exists():
                message = message.decode("utf-8")
                fullpath.write_text(message, encoding="utf-8")
            else:
                print("\tFound email that has already been downloaded. We're done.")
                break

    def delete(self, from_addrs=None, src_folder=None):
        """
        Move messages from email address from_addr
        from src_folder to dst_folder
        """
        if isinstance(from_addrs, str):
            from_addrs = [from_addrs]
        for from_addr in from_addrs:
            print(f"Delete {from_addr}: {src_folder}")
            email_ids = self._matching_emails(self.imap, from_addr, src_folder)
            for i, email_id in enumerate(email_ids):
                logger.info(f'_, data = imap.fetch(str("{email_id}"), "(UID)")')
                _, data = self.imap.fetch(str(email_id), "(UID)")
                msg_uid = self._parse_uid(data[0])
                print(f"\tDeleting {i} of {len(email_ids)}: {msg_uid}")
                self._mail_delete(self.imap, msg_uid)

    def move(self, from_addrs=None, src_folder=None, dst_folder=None, to_addrs=None):
        """
        Move messages from email address from_addr
        from src_folder to dst_folder
        """
        if isinstance(from_addrs, str):
            from_addrs = [from_addrs]
        if isinstance(to_addrs, str) or to_addrs is None:
            to_addrs = [to_addrs]
        logger.info("from %s", from_addrs)
        logger.info("to %s", to_addrs)
        for i, from_addr in enumerate(from_addrs):
            logger.info(f"Move {i} of {len(from_addrs)}: {src_folder} to {str(dst_folder)}")
            for to_addr in to_addrs:
                email_ids = self._matching_emails(self.imap, from_addr, src_folder, to_addr)
                logger.info(f"{len(email_ids)} to move")

                for email_id in email_ids:
                    _, data = self.imap.fetch(str(email_id), "BODY[HEADER.FIELDS (SUBJECT)]")
                    subject = data[0][1]

                    _, data = self.imap.fetch(str(email_id), "(UID)")
                    msg_uid = self._parse_uid(data[0])
                    self._mail_move(self.imap, msg_uid, dst_folder, subject=subject)

    @staticmethod
    def _matching_emails(imap, from_addr, src_folder, to_addr=None):
        src_folder = src_folder or 'INBOX'
        if to_addr:
            # verb = '(AND (TO "{0}")(FROM "{1}"))'.format(to_addr, from_addr)
            # verb = '(TO "{0}" FROM "{1}")'.format(to_addr, from_addr)
            verb = f'(TO "{to_addr}")'
        else:
            verb = f'(FROM "{from_addr}")'

        logger.info(f"imap.select('{src_folder}', readonly=False)")
        imap.select(mailbox=src_folder, readonly=False)

        logger.info(f"_, data = imap.search(None, '{verb}')")
        _, data = imap.search(None, verb)
        return MapEngine._data_ids(data)

    @staticmethod
    def _matching_folder(imap, src_folder):
        """
        You need to select a mailbox after connecting successfully to the IMAP-Server. Use
            m.select()
        after connecting and before search.
        """
        logger.info(f"imap.select({src_folder})")
        imap.select(src_folder, readonly=False)

        logger.info("imap.search(None, ALL)")
        _, data = imap.search(None, "ALL")
        return MapEngine._data_ids(data)

    @staticmethod
    def _data_ids(data):
        if not data or not data[0]:
            return []
        try:
            # Reverse sort -- something unstable about using ascending numbers?
            return sorted((int(x) for x in data[0].split()), reverse=True)
            # return sorted((int(x) for x in data[0].split()))
        except ValueError as val:
            print('-' * 30)
            print(f"_data_ids({data})")
            # return []
            print(val)
            raise
        except Exception as exc:
            print('-' * 30)
            print(f"_data_ids({data})")
            print(exc)
            raise

    @staticmethod
    def _mail_delete(imap, msg_uid):
        logger.info(f"imap.uid('STORE', '{msg_uid}', '+FLAGS', '(\\Deleted)')")
        imap.uid('STORE', msg_uid, '+FLAGS', r'(\Deleted)')
        logger.info('imap.expunge()')
        imap.expunge()

    @staticmethod
    def _mail_move(imap, msg_uid, dst_folder, **kwargs):
        logger.info(
            f'imap.uid("MOVE", {msg_uid}, "{str(dst_folder)})'
        )
        logger.info(f'subject = {kwargs["subject"]}')
        imap.uid('MOVE', msg_uid, f'"{str(dst_folder)}"')

    @staticmethod
    def _parse_uid(data):
        try:
            if isinstance(data, bytes):
                data = data.decode('utf8')
            match = MapEngine.PATTERN_UID.match(data)
            return match.group('uid')
        except Exception as exc:
            print(f"Error in _parse_uid({data}): {exc}")
            raise
