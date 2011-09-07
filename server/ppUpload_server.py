#!/usr/bin/env python
# Copyright (c) 2011, Johan Haals <johan.haals@gmail.com>
# All rights reserved.

import os
import hashlib
import sqlite3
import re
import ConfigParser as configparser
from flask import Flask, request, send_from_directory
from werkzeug import secure_filename
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime
from password import Password

config = configparser.RawConfigParser()
if not config.read([os.path.expanduser('~/.ppupload.conf') or 'ppupload.conf', '/etc/ppupload.conf']):
    sys.exit("Couldn't read configuration file")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.get('settings', 'storage_path')
app.config['DATABASE'] = config.get('settings', 'database_path')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        file = request.files['file']
        username = request.form['username']
        password = request.form['password']
        download_password = request.form['download_password']
        expire = '0'
        one_time_download = '0'
        
        # connect to sqlite and check if user exists
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.execute("select id, password from users where username='%s'" % (username))
        
        try:
            user_id, password_hash = c.fetchone()
        except TypeError:        
            return 'Error: Check username/password'
        
        pw = Password(config.get('settings', 'secret_key'))

        if not pw.validate(password_hash,password):
            return 'Invalid username/password'
        
        allowed_expires = {
            '1h': datetime.now() + relativedelta(hours=1),
            '1d': datetime.now() + relativedelta(days=1),
            '1w': datetime.now() + relativedelta(weeks=1),
            '1m': datetime.now() + relativedelta(months=1),
        }

        if request.form['expire'] in allowed_expires:
            expire = allowed_expires[request.form['expire']].strftime('%Y%m%d%H%M')
            
        if request.form['one_time_download'] == '1':
            one_time_download = '1'

        if download_password:
            download_password = pw.generate(download_password)

        # Generate download hash
        filename = secure_filename(os.path.basename(file.filename))
        download_hash = hashlib.sha1(filename+datetime.now().strftime('%f')).hexdigest()

        # Create a directory based on download_hash and save uploaded file to that folder
        try:
            os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], download_hash))
        except IOError:
            return 'Could not upload file'

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], download_hash, filename))

        # save info to database
        c.execute("""insert into files (hash, user_id, filename, expire, one_time_download, download_password)
          values ('%s','%s','%s','%s', '%s', '%s')""" % (download_hash, user_id, filename, expire, one_time_download, download_password)) 
        conn.commit()
        c.close()

        # everything ok, return download url to client
        return download_hash

    # TODO
    #   web interface...
    return 'Only POSTING allowed'

@app.route('/download', methods=['GET'])
def download_file():

    download_hash = request.args.get('u')

    if re.search('[^A-Za-z0-9_]', download_hash):
        return 'invalid download hash'

    # connect to sqlite and check if file exists
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute("select expire, one_time_download, filename from files where hash='%s' limit 1" % download_hash)

    try:
        expire, one_time_download, filename = c.fetchone()
    except TypeError:
        # No result from query
        return 'Unknown download hash'
    
    # Serve file, everything is ok
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], download_hash),
                               filename, as_attachment=True)
    
    
if __name__ == "__main__":
    app.run(debug=True)

