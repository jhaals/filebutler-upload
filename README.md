filebutler-upload
==========

Upload script to [python-filebutler](http://github.com/jhaals/python-filebutler "python-filebutler")

Install
---
Download filebutler via pip

    $ pip install -e "git+https://github.com/JHaals/filebutler-upload#egg=filebutler_upload"

Quick configuration tutorial will be prompted upon first run

Usage
---
    $ filebutler.py <file/directory*> <options>

Avaliable options:

    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -1, --onetime         One time download(optional)
    -l LIFETIME, --lifetime=LIFETIME
                Lifetime(optional): 1h, 1d, 1w, 1m
                (hour/day/week/month). Default lifetime is unlimited
    -p PASSWORD, --password=PASSWORD
                Download password(optional)


* Directories will automatically be zip-compressed before upload
