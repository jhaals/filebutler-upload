# Standard library
from ConfigParser import RawConfigParser
from argparse import ArgumentParser
import os
import sys
import tempfile
import zipfile

# Third party
import requests

# Local
from . import clipboard
from .filehandler import Filemanager


def compress(path):
    # Create temporary file
    fd, name = tempfile.mkstemp(suffix='.zip')

    zip = zipfile.ZipFile(name, 'w')

    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))

    zip.close()
    return name


class Application(object):
    def __init__(self):
        self.config = None
        self.options = None

    def configuration_tutorial(self):
        print "Filebutler couldn't detect the configuration file, let's create one together!"
        while 1:

            username = raw_input('Username: ')
            if not len(username):
                continue

            password = raw_input('Password(clear text): ')
            if not len(password):
                continue

            print 'Upload url with trailing slash. eg: http://upload.mysite.com/'
            url = raw_input('url: ')
            if not len(url):
                continue

            print 'Username: %s' % username
            print 'Password: %s' % password
            print 'Upload URL: %s' % url
            answer = raw_input('Is this information correct? [y/n]: ')

            if answer == 'y':
                config_path = os.path.expanduser('~/.filebutler-upload.conf')
                print 'Writing config file to %s' % config_path
                with open(config_path, 'w') as f:
                    f.write('[settings]\n')
                    f.write('username = %s\n' % username)
                    f.write('password = %s\n' % password)
                    f.write('upload_url = %s\n' % url)
            break
        self.read_configuration()

    def read_configuration(self):
        # Search for the configuration file in the following paths.
        paths = [
            os.path.expanduser('~/.filebutler-upload.conf'),
            'filebutler-upload.conf',
            '/etc/filebutler-upload.conf'
        ]

        self.config = RawConfigParser()

        if not self.config.read(paths):
            self.configuration_tutorial()

    def parse_arguments(self):
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        available_commands = []

        # Upload
        parser_upload = subparsers.add_parser('upload')
        parser_upload.add_argument('-1', '--onetime', action='store_const',
            const='1', default='0',
            help='One time download.')

        parser_upload.add_argument('-l', '--lifetime',
            choices=['1h', '1d', '1w', '1m'], default='',
            help='Lifetime: 1h, 1d, 1w, 1m (hour/day/week/month). ' \
                 'Default lifetime is forever.')

        parser_upload.add_argument('-p', '--password', default='',
            help='Make this a password protected file.')

        parser_upload.add_argument('path')
        parser_upload.set_defaults(command='upload')
        available_commands.append('upload')

        # List
        parser_list = subparsers.add_parser('list')
        parser_list.set_defaults(command='list')
        available_commands.append('list')

        # Delete
        parser_delete = subparsers.add_parser('delete')
        parser_delete.add_argument('hash', help='File to delete')
        parser_delete.set_defaults(command='delete')
        available_commands.append('delete')

        arguments = sys.argv[1:]

        if arguments and not arguments[0] in available_commands:
            arguments = ['upload'] + arguments

        self.options = parser.parse_args(arguments)

    def run(self):
        self.read_configuration()
        self.parse_arguments()

        fm = Filemanager(
            self.config.get('settings', 'upload_url'),
            self.config.get('settings', 'username'),
            self.config.get('settings', 'password')
        )

        if self.options.command == 'upload':
            filepath = self.options.path

            if os.path.isdir(filepath):
                filepath = compress(filepath)

            try:
                upload_file = open(filepath, 'rb')
            except IOError:
                print 'Could not open file:', filepath
                return 1

            response = fm.upload(
                upload_file,
                self.options.password,
                self.options.onetime,
                self.options.lifetime
            )

            if response.status_code != requests.codes.ok:
                print 'Failed to upload file. Error {0}: {1}'.format(
                    response.status_code,
                    response.json['message']
                )

                return 1

            url = response.json['message']
            clipboard.copy(url)
            print url

            return 0

        if self.options.command == 'list':
            response = fm.list()

            for hash, name in response.iteritems():
                print hash, name

            return 0

        if self.options.command == 'delete':
            response = fm.delete(self.options.hash)

            return 0

        print 'Unrecognized command'
        return 1
