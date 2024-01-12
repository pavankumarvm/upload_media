from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import psycopg2 
import os

app = Flask(__name__)

BASE_DIR = app.root_path

# Connect to the database 
# conn = psycopg2.connect(database="flask_db", user="postgres", 
#                         password="root", host="localhost", port="5432") 

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'media')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)

@app.route('/', methods=['GET'])
def index():
    return "You are not supposed to be here."

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Save the files
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return make_response(jsonify({'message':'File uploaded successfully'}),200)
            except Exception as e:
                return f'Error saving file: {str(e)}', 500
        elif not allowed_file(file.filename):
            return make_response(jsonify({'message':'File type not allowed.'}), 400)
    else:
        return make_response(jsonify({'message': 'No file found in the request.'}), 400)
    return make_response(jsonify({'message': 'File upload failed.'}), 400)


if __name__ == '__main__': 
	app.run(debug=True) 
