#!/usr/bin/python3
from flask import Flask, render_template, request, send_file, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
from parser import make_data_frame_with_meta_from_list_of_logins


CURRENT_DIR  = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = os.path.join(CURRENT_DIR,'uploads')
app.config['MAX_CONTENT_PATH'] = 20
app.config['PROCESSED_FOLDER'] = os.path.join(CURRENT_DIR, 'processed_files')


@app.route('/upload')
def upload_file():
    uploads = os.listdir(app.config['UPLOAD_FOLDER'])
    processed_files = os.listdir(app.config['PROCESSED_FOLDER'])

    return render_template('upload.html',
                           uploads=uploads,
                           processed_files = processed_files,
                           route_to_file=app.config['UPLOAD_FOLDER'])


@app.route('/download_inputed_file/<path:filename>', methods=['GET'])
def download_inputed_file(filename):
    if request.method == 'GET':
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return send_file(path, as_attachment=True)

@app.route('/download_processed_file/<path:filename>', methods=['GET'])
def download_processed_file(filename):
    if request.method == 'GET':
        path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        return send_file(path, as_attachment=True)


@app.route('/uploader', methods=['GET', 'POST'])
def file_ulpoader():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename.endswith('.txt'):
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))

            with open(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)), 'r') as input_f:
                list_of_logins = input_f.readlines()
            list_of_logins = [x.strip() for x in list_of_logins]
            meta_data = make_data_frame_with_meta_from_list_of_logins(
                list_of_logins)
            
            meta_data.to_excel(
                os.path.join(app.config['PROCESSED_FOLDER'],
                             f'{secure_filename(f.filename)[:-4]}.xlsx'), index = False)
            return redirect(url_for("upload_file"), code=302)
        else:
            return redirect(url_for("upload_file"))

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug = False)