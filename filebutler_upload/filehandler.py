import requests


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
                'username': self.username,
                'password': self.password,
                'download_password': download_password,
                'one_time_download': '1' if one_time_download else '0',
                'expire': expire
            }

        response = requests.post(
            self.url,
            data=data,
            files=files,
            headers=self.headers
        )

        return response
