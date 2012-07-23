# Standard library
from ConfigParser import RawConfigParser
from optparse import OptionParser
import os
import sys
import tempfile
import zipfile

# Third party
import requests

# Local
from filebutler_upload import clipboard


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
        self.args = []
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
        parser = OptionParser('usage: %prog -h', version="%prog 0.1")

        parser.add_option("--onetime", "-1", help='One time download', \
            default=False, action='store_true')

        parser.add_option("--lifetime", "-l",
            choices=('', '1h', '1d', '1w', '1m'), default='',
            help='Lifetime: 1h, 1d, 1w, 1m (hour/day/week/month). ' \
            'Default lifetime is unlimited')

        parser.add_option("--password", "-p", default='',
            help='Download password')

        self.options, self.args = parser.parse_args()

        if not len(self.args):
            parser.error('Please specify atleast one file to upload.')

    def run(self):
        self.read_configuration()
        self.parse_arguments()

        filepath = self.args[0]

        if os.path.isdir(filepath):
            # Compress directory
            filepath = compress(filepath)

        try:
            upload_file = open(filepath, 'rb')
        except IOError:
            sys.exit('Could not open file: ' + filepath)

        # Prepare the data
        headers = {'Accept': 'application/json'}
        files = {'file': upload_file}
        data = {
                'username': self.config.get('settings', 'username'),
                'password': self.config.get('settings', 'password'),
                'download_password': self.options.password,
                'one_time_download': '1' if self.options.onetime else '0',
                'expire': self.options.lifetime
            }

        response = requests.post(
            self.config.get('settings', 'upload_url'),
            data=data,
            files=files, headers=headers
        )

        if response.status_code is 200:
            clipboard.copy(response.json['message'])
            print response.json['message']
            return 0

        else:
            print 'Failed to upload file. Error %s: %s' % (
                    response.status_code,
                    response.json['message'])
            return 1
