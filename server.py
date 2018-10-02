import os, random, struct
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES

app = Flask(__name__, static_url_path='/uploadFolder')

UPLOAD_FOLDER = '/uploadFolder'

def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):

    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'file' not in request.files:
        return "You must upload file"
    
    file = request.files['file']
    if (file.filename == ''):
        return "No select file"

    file.save('uploadFolder/'+file.filename)
    encrypt_file("bui xuan thuyMTA", 'uploadFolder/'+file.filename)

    return send_from_directory('uploadFolder',file.filename+'.enc') 

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'file' not in request.files:
        return "You must upload file"
    
    file = request.files['file']
    if (file.filename == ''):
        return "No select file"

    file.save('uploadFolder/'+file.filename)
    decrypt_file("bui xuan thuyMTA",'uploadFolder/'+file.filename, 'uploadFolder/a'+file.filename)

    print('success')

    return send_from_directory('uploadFolder', 'a'+file.filename) 

if __name__ == '__main__':
    app.run(debug=True)