import requests
#import os
#from ConfigParser import RawConfigParser
#from text_table import TextTable


class Filemanager:
    def __init__(self, url, username, password):
        self.headers = {'Accept': 'application/json'}
        self.username = username
        self.password = password
        self.url = url

    def list(self):
        '''
        List all files uploaded by user
        '''
        data = {
                'username': self.username,
                'password': self.password
            }

        response = requests.post(
            self.url + 'files',
            data=data,
            headers=self.headers
        )

        if response.status_code == 200:
            return response.json['message']
        else:
            return {}

    def delete(self, hash):
        ''' delete specified hash '''
        if hash == 'all':
            pass

        data = {
                'username': self.username,
                'password': self.password,
            }

        response = requests.post(
            self.url + hash + '/delete',
            data=data,
            headers=self.headers
        )

        return response.text

    def upload(self, upload_file,
        download_password, one_time_download, expire):

        files = {'file': upload_file}
        data = {
                'username': self.config.get('settings', 'username'),
                'password': self.config.get('settings', 'password'),
                'download_password': self.options.password,
                'one_time_download': '1' if self.options.onetime else '0',
                'expire': self.options.lifetime
            }

        response = requests.post(
            self.url,
            data=data,
            files=files, headers=self.headers
        )

        return response


# For testing, remove when finished.
#config = RawConfigParser()
#config.read(os.path.expanduser('~/.filebutler-upload.conf'))

#username = config.get('settings', 'username')
#password = config.get('settings', 'password')
#url = config.get('settings', 'upload_url')

#fm = Filemanager(url, username, password)


#t = TextTable((40, 'Download hash'), (35, 'Filename'))
#for hash, filename in fm.list().iteritems():
#    t.row(hash, filename)
#print t.draw()

print fm.delete('a13170f4cdbd96743e18126306ddba484785ba6b')
