from httputils import post
from utils import ProgressBar
from urlparse import urljoin

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

        status, response = post(urljoin(self.url, 'files'), data, self.headers)

        return status, response

    def delete(self, hash):
        ''' delete specified hash '''
        if hash == 'all':
            pass

        data = {
            'username': self.username,
            'password': self.password,
        }

        status, response = post(self.url + hash + '/delete',
                data = data,
                headers=self.headers)

        return status, response

    def upload(self, upload_file, download_password, one_time_download, expire):
        data = {
            'username': self.username,
            'password': self.password,
            'download_password': download_password,
            'one_time_download': '1' if one_time_download else '0',
            'expire': expire,
            'file': upload_file
        }

        pb = ProgressBar(upload_file.name, '{filename} {percent:.1%} {speed:.1f} mbps')
        status, response = post(self.url, data, self.headers, callback=pb)

        return status, response
