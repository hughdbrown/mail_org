#/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='mail_org',
    version='0.1',
    description='Application to perform batch operations on email accounts using IMAP4',
    author='Hugh Brown',
    author_email='hughdbrown@yahoo.com',
    url='hughdbrown.com',
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'simplejson'
    ],
    setup_requires=[],
    packages=[
        'src',
    ],
    zip_safe=False,
)
