# mail_org
A python script for performing bulk operations against an email account using IMAP4

I use this python code to clean up my inbox, moving messages to subfolders or just deleting them.

The `mail-org.json` gives a good idea of what you can do.

# Deletion
Delete all messages from your Inbox that are from `from_addr`.
```
    {
        "optype": "delete",
        "from_addr": "info@mail.HealthcareJobInsider.com",
        "src_folder": "Inbox"
    }
```

# Move
Move all messages from your Inbox from `from_addr` and move them to `dst_folder`.
```
    {
        "optype": "move",
        "from_addr": "jobs-listings@linkedin.com",
        "dst_folder": "linkedin.com - jobs",
        "src_folder": "Inbox"
    }
```


#Installation
```
python setup.py install --user --prefix=
```
Using `prefix is a bit of a kludge to get around a bug on OSX.
