filebutler-upload
==========

Upload script to [python-filebutler](http://github.com/jhaals/python-filebutler "python-filebutler")

Install
---

Install python requirements:

        pip install -r requirements.txt
Configure filebutler-upload.conf and place it under ~/.filebutler-upload.conf or /etc/

It's recommended to place an alias for filebutler in your .bashrc or similar.

Usage
---
    filebutler.py <file> <options>

Avaliable options:

    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -1, --onetime         One time download(optional)
    -l LIFETIME, --lifetime=LIFETIME
                Lifetime(optional): 1h, 1d, 1w, 1m
                (hour/day/week/month). Default lifetime is unlimited
    -p PASSWORD, --password=PASSWORD
                Download password(optional)
