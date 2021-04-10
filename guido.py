#!flask/bin/python
from flask import Flask, request, send_from_directory
import fawkes.protection as p
import hashlib, uuid, threading, os
import json, base64

QUALITY = 'low'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'pictures/'
active_threads = dict()



@app.route('/upload/', methods=['POST'])
def get_image_from_client():
    json_body = request.get_json()
    photo = json_body['photo']
    uid = str(uuid.uuid4().int)
    folder = app.config['UPLOAD_FOLDER'] + uid + '/'
    os.mkdir(folder)
    with open(os.path.join(folder , uid+ '.png'), 'w') as photo_file:
        photo_file.write(photo)
    tempThread = threading.Thread(target=run_protection, args=(folder,))
    active_threads[uid] = tempThread
    tempThread.start()
    print('UID: ', uid)
    return uid

def run_protection(folder):
    p.main('','-d', folder , '-m', QUALITY, '--no-rename-file')




@app.route('/fetch/', methods=['POST'])
def get_image_from_server():
    json_body = request.get_json()
    uid = json_body['uid']
    print("\n\n\n\nREQUEST HAS UID " + uid)
    print(active_threads)
    if uid not in active_threads.keys():
        return 'failed'
    if active_threads[uid].is_alive():
        return 'pending'
    img_path = app.config['UPLOAD_FOLDER'] + uid + '/' + uid + '.png'
    with open(img_path, 'rb') as img_file:
            img = img_file.read()
    b64_img = base64.b64encode(img)
    with open(img_path, 'wb') as img:
        img.write(b64_img)
    return send_from_directory(app.config['UPLOAD_FOLDER'] + uid + '/', uid + '.png', as_attachment=True)


if __name__ == '__main__':
    #app.run('192.168.0.118', port='8008', debug=True, ssl_context=('server.crt', 'server.key'))
    app.run('192.168.0.119', port='8080', debug=True)