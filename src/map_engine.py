"""
Implementation of class to perform mass operations on imap account
"""
from __future__ import print_function

import imaplib
import re

import simplejson


class IMapEngine(object):
    """
    Class for mass operations on imap accounts
    """
    PATTERN_UID = re.compile(r'''\d+ \(UID (?P<uid>\d+)\)''')

    def __init__(self, host, username, password):
        """
        Constructor
        """
        self.imap = imaplib.IMAP4_SSL(host)
        self.imap.login(username, password)

    def __enter__(self):
        """
        __enter__ method for context manager
        """
        return self

    def __exit__(self, _type, value, traceback):
        """
        __exit__ method for context manager
        """
        self.imap.close()
        self.imap.logout()

    def apply(self, filename):
        """
        Apply a file of commands to the account
        """
        try:
            with open(filename) as handle:
                objs = simplejson.loads(handle.read())

            for obj in objs:
                optype = obj.pop("optype")
                if optype == 'move':
                    self.move(**obj)
                elif optype == 'delete':
                    self.delete(**obj)
        except Exception as exc:  # pylint: disable=broad-except
            print(exc)

    def delete(self, from_addr=None, src_folder=None):
        """
        Move messages from email address from_addr
        from src_folder to dst_folder
        """
        print("Delete {1}: {0}".format(src_folder, from_addr))
        email_ids = self._matching_emails(self.imap, from_addr, src_folder)
        for email_id in email_ids:
            _, data = self.imap.fetch(str(email_id), "(UID)")
            msg_uid = self._parse_uid(data[0])
            print("\tDeleting {0}".format(msg_uid))
            self._mail_delete(self.imap, msg_uid)

    def move(self, from_addr=None, src_folder=None, dst_folder=None):
        """
        Move messages from email address from_addr
        from src_folder to dst_folder
        """
        print("Move {2}: {0} to {1}".format(src_folder, dst_folder, from_addr))
        email_ids = self._matching_emails(self.imap, from_addr, src_folder)
        for email_id in email_ids:
            _, data = self.imap.fetch(str(email_id), "(UID)")
            msg_uid = self._parse_uid(data[0])
            self._mail_move(self.imap, msg_uid, dst_folder)

    @staticmethod
    def _matching_emails(imap, from_addr, src_folder):
        verb = '(FROM "{0}")'.format(from_addr)
        imap.select(src_folder, readonly=False)
        _, data = imap.search(None, verb)

        # Reverse sort -- something unstable about using ascending numbers?
        return sorted((int(x) for x in data[0].split()), reverse=True)

    @staticmethod
    def _mail_delete(imap, msg_uid):
        imap.uid('STORE', msg_uid, '+FLAGS', r'(\Deleted)')
        imap.expunge()

    @staticmethod
    def _mail_move(imap, msg_uid, dst_folder):
        print("\tCopying/deleting {0}".format(msg_uid))
        result = imap.uid('COPY', msg_uid, dst_folder)
        if result[0] == 'OK':
            IMapEngine._mail_delete(imap, msg_uid)
        else:
            print(result)

    @staticmethod
    def _parse_uid(data):
        match = IMapEngine.PATTERN_UID.match(data)
        return match.group('uid')
