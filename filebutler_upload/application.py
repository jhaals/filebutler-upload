# Standard library
from ConfigParser import RawConfigParser
from argparse import ArgumentParser
from contextlib import closing
from zipfile import ZipFile
import json
import os
import sys
import tempfile

# Local
from . import clipboard
from .filehandler import Filemanager


def compress(path):
    # Make sure that we work with an absolute path
    path = os.path.abspath(path)

    _fd, tempfile_path = tempfile.mkstemp()

    # Get the parent of the given directory. This will be used to give the
    # archived files their relative names.
    parent, _directory = os.path.split(path)

    with closing(ZipFile(tempfile_path, 'w')) as zipfile:

        # Traverse recursively through the target directory.
        for root, dirs, files in os.walk(path):

            # Strip the preceding path to the target directory
            archive_root = root.replace(parent, '')

            for filename in files:
                archive_filename = os.path.join(archive_root, filename)
                zipfile.write(os.path.join(root, filename), archive_filename)

    return tempfile_path


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

        # Upload
        parser_upload = subparsers.add_parser('upload')
        parser_upload.add_argument('-1', '--onetime', action='store_true',
            help='One time download.')

        parser_upload.add_argument('-l', '--lifetime',
            choices=['1h', '1d', '1w', '1m'], default='',
            help='Lifetime: 1h, 1d, 1w, 1m (hour/day/week/month). ' \
                 'Default lifetime is forever.')

        parser_upload.add_argument('-p', '--password', default='',
            help='Make this a password protected file.')

        parser_upload.add_argument('path')
        parser_upload.set_defaults(command=self.do_upload)

        # List
        parser_list = subparsers.add_parser('list')
        parser_list.set_defaults(command=self.do_list)

        # Delete
        parser_delete = subparsers.add_parser('delete')
        parser_delete.add_argument('hash', help='File to delete')
        parser_delete.set_defaults(command=self.do_delete)

        arguments = sys.argv[1:]
        positional = filter(
            lambda x: not x.startswith('-'), arguments
        )

        if len(positional) >= 1 and not positional[0] in subparsers.choices.keys():
            arguments = ['upload'] + arguments

        self.options = parser.parse_args(arguments)

    def do_upload(self, fm):
        filepath = self.options.path

        if os.path.isdir(filepath):
            filepath = compress(filepath)

        try:
            upload_file = open(filepath, 'rb')
        except IOError:
            print 'Could not open file:', filepath
            return 1

        status_code, response = fm.upload(
            upload_file,
            self.options.password,
            self.options.onetime,
            self.options.lifetime
        )

        response = json.loads(response)

        if status_code != 200:
            print 'Failed to upload file. Error {0}: {1}'.format(
                status_code,
                response['message']
            )

            return 1

        url = response['message']
        clipboard.copy(url)
        print url

        return 0

    def do_list(self, fm):
        status_code, response = fm.list()

        response = json.loads(response)

        if status_code != 200:
            print 'Failed to list file. Error {0}: {1}'.format(
                status_code,
                response['message']
            )

            return 1

        for hash, data in response['message'].iteritems():
            print hash, data['filename']
        return 0

    def do_delete(self, fm):
        status_code, response = fm.delete(self.options.hash)

        response = json.loads(response)

        if status_code != 200:
            print 'Failed to delete file. Error {0}: {1}'.format(
                status_code,
                response['message']
            )
            return 1

        return 0

    def run(self):
        self.read_configuration()
        self.parse_arguments()

        fm = Filemanager(
            self.config.get('settings', 'upload_url'),
            self.config.get('settings', 'username'),
            self.config.get('settings', 'password')
        )

        return self.options.command(fm)
