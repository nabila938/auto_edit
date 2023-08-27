from flask import Flask, request, render_template, jsonify, Response, redirect, url_for
from pymongo import MongoClient
import os
from io import StringIO
import html
import shutil
import zipfile

from os.path import dirname, join
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_HOST = os.environ.get("MONGODB_URL")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(DB_HOST)
db = client[DB_NAME]


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def test(username):
    user_data = db.user.find_one({'username': 'sayoga'}, {'_id': False})

    return user_data

def duplikat_folder(username, filename):

    source_directory = f'file joki/{filename}'
    destination_directory = f'file_proses/{filename}'

    user_data = getdataByName(username)

    mongoDbUrl = user_data.get("mongodbUrl")
    dbname = user_data.get("dbname")


    shutil.copytree(source_directory, destination_directory)

    file_path = f'file_proses/{filename}/app.py'

    # Buka file dalam mode tulis ('w')
    with open(file_path, 'r') as file:
        content = file.read()

    # Lakukan pengeditan pada konten file
    new_content = content.replace('$', mongoDbUrl).replace('dbname', dbname)

    # Buka file dalam mode tulis ('w') untuk menyimpan konten yang sudah diubah
    with open(file_path, 'w') as file:
        file.write(new_content)

    # Mengarsipkan folder 'file joki/minggu' menjadi file zip setelah dimodifikasi
    shutil.make_archive(f'final_file_joki/{filename}_{username}', 'zip', 'file_proses', filename)

    folder_path = f'file_proses/{filename}'
    shutil.rmtree(folder_path)


    # Siapkan response dengan header untuk mengunduh
    response = Response(
        open(f'final_file_joki/{filename}_{username}.zip', 'rb').read(),
        content_type='application/zip'
    )
    response.headers["Content-Disposition"] = f"attachment; filename={filename}_{username}.zip"

    return response



@app.route('/download', methods=['POST'])
def modify_and_download():

    
    username = request.form.get('user')
    filename = request.form.get('tugas')

    return duplikat_folder(username, filename)

    # duplikat_folder(username, filename)
    
    """# Baca isi file app.py dan simpan sebagai file cadangan sebelum dimodifikasi
    file_path = 'file joki/minggu3/app.py'
    with open(file_path, 'r') as file:
        original_content = file.read()

    # Mengarsipkan folder 'file joki/minggu' menjadi file zip sebagai cadangan
    shutil.make_archive('original_minggu', 'zip', 'file joki/minggu3')

    # Modifikasi konten dengan mengganti $$ menjadi string yang diinputkan
    modified_content = original_content.replace('$dbhost', 'anjash')

    # Simpan konten yang sudah dimodifikasi kembali ke file
    with open(file_path, 'w') as file:
        file.write(modified_content)

    # Mengarsipkan folder 'file joki/minggu' menjadi file zip setelah dimodifikasi
    shutil.make_archive('modified_minggu', 'zip', 'file joki/minggu')

    # Pindahkan file zip yang sudah dibuat ke dalam folder 'final_file_joki'
    shutil.move('modified_minggu.zip', 'final_file_joki/modified_minggu.zip')

    # Mengembalikan file app.py ke kondisi semula dari file cadangan
    with open('original_minggu.zip', 'rb') as zip_file:
        shutil.unpack_archive(zip_file.name, extract_dir='file joki/minggu', format='zip')

    # Siapkan response dengan header untuk mengunduh
    response = Response(
        open('final_file_joki/modified_minggu.zip', 'rb').read(),
        content_type='application/zip'
    )
    response.headers["Content-Disposition"] = "attachment; filename=modified_minggu.zip"

    return response"""

def ekstrak_file(filename):

    # Path arsip yang ingin diekstrak
    path_arsip = f'zipfile/{filename}'

    # Path tujuan ekstraksi
    path_ekstraksi = f'file joki/{filename.split(".")[0]}'
    
    # Ekstrak arsip
    shutil.unpack_archive(path_arsip, path_ekstraksi)

    os.remove(f'zipfile/{filename}')



@app.route('/tambahUser')
def tambahUser():
    return render_template('tambah_user.html')

@app.route('/tambah_user', methods=['POST'])
def addUser():
    username = html.escape(request.form.get('username'))
    mongodb_url = html.escape(request.form.get('mongodb-url'))
    dbname = html.escape(request.form.get('dbname'))

    doc = {
        'username': username,
        'mongodbUrl': mongodb_url,
        'dbname': dbname
    }

    db.user.insert_one(doc)

    return redirect(url_for('tambahUser'))

def getdataByName(username):
    data = db.user.find_one({'username': username}, {'_id': False})
    return data


@app.route('/getData', methods=['GET'])
def getUser():

    collection_name = request.args.get('collection')

    collection = db[collection_name]

    data = collection.find({}, {'_id': False})

    user_list = list(data)

    return user_list

@app.route('/add_file')
def add_file():
    return render_template('add_tugas.html')

@app.route('/save_file', methods=['POST'])
def save_file():
    file = request.files['file-tugas']
    tugasName = request.form.get('nama-tugas')
    keterangan = request.form.get('keterangan')

    filename = file.filename

    file.save(f'zipfile/{filename}')

    db.file_tugas.insert_one({
        'fileName': filename.split(".")[0],
        'tugasName': tugasName,
        'keterangan': keterangan
    })

    ekstrak_file(filename)

    return redirect(url_for('add_file'))


# @app.route('/download_tugas')
# def download_tugas():
#     return

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
