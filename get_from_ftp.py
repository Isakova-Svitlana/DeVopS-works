#!/usr/bin/python

import ftplib
import os

path = '/var/tftp/huawei'
filename = '172.19.22.3.cfg'

ftp = ftplib.FTP("62.122.200.28")
ftp.login("kbn", "hfdYMCmi")
ftp.cwd(path)
res = ftp.retrbinary("RETR " + filename, open(filename, 'wb').write)

if not res.startswith('226 Transfer complete'):
    print('Downloaded of file {0} is not compile.'.format(filename))
    os.remove(filename)

ftp.quit()
