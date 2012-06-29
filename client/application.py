# Standard library
from ConfigParser import RawConfigParser
from optparse import OptionParser
import os
import sys

# Third party
import requests

# Local
import clipboard


class Application(object):
    def __init__(self):
        self.args = []
        self.config = None
        self.options = None

    def read_configuration(self):
        # Search for the configuration file in the following paths.
        paths = [
            os.path.expanduser('~/.ppupload.conf'),
            'ppupload.conf',
            '/etc/ppupload.conf'
        ]

        self.config = RawConfigParser()

        if not self.config.read(paths):
            sys.exit("Couldn't read configuration file")

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

        if not os.path.isfile(filepath):
            sys.exit('Does not exist: ' + filepath)

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

        if response:
            clipboard.copy(response.json['message'])

            print response.json['message']
            return 0

        else:
            print 'Request failed with status code:', response.status_code
            print response.json['message']
            return 1
