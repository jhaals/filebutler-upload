#!/usr/bin/env python

import sys

from filebutler_upload.application import Application


def main():
    instance = Application()
    sys.exit(instance.run())


if __name__ == '__main__':
    main()
