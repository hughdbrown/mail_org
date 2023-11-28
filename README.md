# mail_org
A python script for performing bulk operations against an email account using IMAP4

I use this python code to clean up my inbox, moving messages to subfolders or just deleting them.

The `mail-org.json` gives a good idea of what you can do.

# Required files

## .env
You need to add a file `.env` with your email credentials. The keys are:
```
EMAIL_HOST=...
EMAIL_USERNAME=...
EMAIL_PASSWORD=...
```

For Yahoo, you can create an application-specific password.

The host name I use for Yahoo mail is `imap.n.mail.yahoo.com`. You will have to look up the imap server name used for your email service.

## mail-org.json
You need a JSON file that tells your `mail-org` what to do with varieties of email. The main actions are to archive messages to a folder (like, move from
Inbox to another folder) or to delete the matching messages. You can also make a file backup to a file location.

The general format of the JSON file is a list of comma-separated dictionaries:
```
[
    {...verb-specific layout...}
]
```
The list of actions can be as long as you like (i.e. as many dictionaries as desired) but they have to be comma-separarted and the lat One has no
trailing comma.

# Verbs

## Download
Move the latest email messages in an email folder to file in a directory on disk.
```
  {
    "optype": "download",
    "src_folder": "@job_search",
    "dst_dir_name": "~/email/job-search"
  }
```

In this example, all the messages I have moved from my `Inbox` to my folder `@job_search` are saved to the directory `~/email/job-search/`.

## Deletion
Delete all messages from your Inbox that are from `from_addr`.
```
    {
        "optype": "delete",
        "from_addr": "info@mail.HealthcareJobInsider.com",
        "src_folder": "Inbox"
    }
```



## Move
Move all messages from your Inbox from `from_addr` and move them to `dst_folder`.
```
    {
        "optype": "move",
        "from_addr": "jobs-listings@linkedin.com",
        "dst_folder": "linkedin.com - jobs",
        "src_folder": "Inbox"
    }
```


# Installation
```
python setup.py install --user --prefix=
```
Using `prefix` is a bit of a kludge to get around a bug on OSX.

Alternatively, set up a virtualenv and run from this directory:
```
# Make the virtualenv
pyenv virtualenv 3.12.0 email-org-3.12.0

# Make the virtualenv activate when directory is entered
pyenv local email-org-3.12.0

# Install pip and requirements
pip install --upgrade pip
pip install -r requirements.txt
```
