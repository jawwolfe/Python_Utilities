from ftplib import FTP
import zipfile
import os
import sys
import glob
import base64

########### MODIFY ########################
USER = 'ftp_one'
PASS_bytes = base64.b64decode(open('C:/utility.txt', 'r').read())
PASS = PASS_bytes.decode("utf8")
########### MODIFY IF YOU WANT ############
SERVER = 'www.daconsol.com'
PORT = 21
BINARY_STORE = True  # if False then line store (not valid for binary files (videos, music, photos...))
###########################################
path = 'C:\\backups\\'
databases = ['DCS', 'Garden', 'Chameleon']
###########################################

def print_line(result):
    print(result)

def connect_ftp():
    # Connect to the server
    ftp = FTP()
    ftp.connect(SERVER, PORT)
    ftp.login(USER, PASS)
    ftp.set_pasv(False)
    return ftp

def upload_file(ftp_connetion, upload_file_path):
    # Open the file
    try:
        upload_file = open(upload_file_path, 'rb')

        # get the name
        path_split = upload_file_path.split('/')
        final_file_name = path_split[len(path_split) - 1]

        # transfer the file
        print('Uploading ' + final_file_name + '...')

        if BINARY_STORE:
            ftp_connetion.storbinary('STOR ' + final_file_name, upload_file)
        else:
            # ftp_connetion.storlines('STOR ' + final_file_name, upload_file, print_line)
            ftp_connetion.storlines('STOR ' + final_file_name, upload_file)

        print('Upload finished.')

    except IOError:
        print("No such file or directory... passing to next file")

# Take all the files and upload all
ftp_conn = connect_ftp()

for database in databases:
    files = glob.glob(path + database + '\\*.BAK')
    myfile = max(files , key = os.path.getctime)
    myzip = myfile[:-4] + '.zip'
    zip = zipfile.ZipFile(myzip, "w", zipfile.ZIP_DEFLATED)
    zip.write (myfile)
    zip.close()
    upload_file(ftp_conn, myzip.replace('\\','/'))

#clean up by removing all zip files after ftp to backup server
filelist = [ f for f in os.listdir(path) if f.endswith(".zip") ]
for f in filelist:
    os.remove(path + f)

print("success")