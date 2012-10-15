#!/usr/bin/env python

import sys

from filebutler_upload.application import Application


if __name__ == '__main__':
    instance = Application()
    sys.exit(instance.run())
