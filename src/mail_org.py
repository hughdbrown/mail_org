#!/usr/bin/env python
'''
Driver program for map_engine.py

User Name:User@yahoo.com
Password: Password of your yahoo mail
Incoming mail server: imap.n.mail.yahoo.com
Mailbox Name: Yahoo
Mailbox type: IMAP4
Security(Ports): Off
Port: Default
'''

from __future__ import print_function


import getpass

from map_engine import IMapEngine


def main():
    """
    Main entry point
    """
    host = 'imap.n.mail.yahoo.com'
    username = 'hughdbrown@yahoo.com'
    password = getpass.getpass()
    with IMapEngine(host, username, password) as i:
        i.apply("mail-org.json")


if __name__ == '__main__':
    main()
