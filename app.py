from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import psycopg2 
import os

app = Flask(__name__)

BASE_DIR = app.root_path

# Connect to the database 
def db_connect():
    conn = psycopg2.connect(database="verceldb", user="default", 
                        password="e1L2CNmZJVhx", host="ep-restless-cell-26446902-pooler.ap-southeast-1.postgres.vercel-storage.com", port="") 
    cur = conn.cursor()
    return conn,cur

def db_disconnect(conn, cur):
    cur.close()
    conn.close()

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'media/images')

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
    if request.method=='POST':
        try:
            if 'images' in request.files:
                current_url = request.form['current_url']
                name = request.form['imageTitle']
                image_type = request.form['image_type']
                images = request.files.getlist('images')
                if current_url.split("/")[-2] == "tc":
                    name = name +"-(" + request.form('studentStd') + ")"
                conn,cur=db_connect()
                cur.execute('''SELECT COUNT(*) FROM Images WHERE image_type=%s''', (image_type))       
                # Fetch the data 
                data = cur.fetchall()
                print(data)
                cnt=data+1
                for file in images:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        # Save the files
                        try:
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            cur.execute('''INSERT INTO IMAGES \
                                        (name, image, image_type, sequence_no) VALUES\
                                        (%s, %s, %s, %s)
                                        ''',
                                        (name, f'images/{filename}', image_type, cnt))
                            conn.commit()
                            db_disconnect(conn,cur)
                            return make_response(jsonify({'message':'Images uploaded successfully'}),200)
                        except Exception as e:
                            db_disconnect(conn,cur)
                            return f'Error saving file: {str(e)}', 500
                    elif not allowed_file(file.filename):
                        db_disconnect(conn,cur)
                        return make_response(jsonify({'message':'File type not allowed.'}), 400)
            else:
                return make_response(jsonify({'message': 'No images found in the request.'}), 400)
        except Exception as e:
            return make_response(jsonify({'message': 'Images upload failed.','error': e}), 400)

@app.route('/delete', methods=['POST']) 
def delete(): 
    conn, cur = db_connect()
    current_url = request.form['current_url']
    images_to_delete = request.form['images_to_delete']
    images_to_delete = images_to_delete.split(",")
    for image_id in images_to_delete:
        # Delete the data from the table 
        cur.execute('''DELETE FROM Images WHERE id=%s''', (image_id,)) 
  
    # commit the changes 
    conn.commit() 

    db_disconnect(conn,cur) 
  
    return redirect(url_for('index')) 
if __name__ == '__main__': 
	app.run(debug=True) 
