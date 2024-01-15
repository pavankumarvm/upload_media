from flask import Flask, request, jsonify, make_response
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
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'media\images')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)

@app.route('/', methods=['GET'])
def index():
    return "You are not supposed to be here.<br/><br/>If any queries, kindly mail to: pavankumarmaurya1999@gmail.com."

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
                cur.execute(f'SELECT COUNT(*) FROM public."Image" WHERE image_type=\'{image_type}\'')       
                # Fetch the data 
                data = cur.fetchall()
                cnt=data[0][0]+1
                for file in images:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        # Save the files
                        try:
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            cur.execute(f'''INSERT INTO public."Image" \
                                        (name, image, image_type, sequence_no) VALUES\
                                        (\'{name}\', \'images/{filename}\', \'{image_type}\', \'{cnt}\')
                                        ''')
                            cnt+=1
                        except Exception as e:
                            db_disconnect(conn,cur)
                            return f'Error saving file: {str(e)}', 500
                    elif not allowed_file(file.filename):
                        db_disconnect(conn,cur)
                        return make_response(jsonify({'message':'File type not allowed.'}), 400)
                conn.commit()
                db_disconnect(conn,cur)
                return make_response(jsonify({'message':'Images uploaded successfully'}),200)
            else:
                return make_response(jsonify({'message': 'No images found in the request.'}), 400)
        except Exception as e:
            db_disconnect(conn,cur)
            return make_response(jsonify({'message': 'Images upload failed.','error': e}), 400)

@app.route('/delete', methods=['POST']) 
def delete(): 
    try:
        conn, cur = db_connect()
        current_url = request.form['current_url']
        images_to_delete = request.form['images_to_delete']
        images_to_delete = images_to_delete.split(",")
        for image_id in images_to_delete:
            # Delete the data from the table
            cur.execute(f'''SELECT * FROM public."Image" WHERE id=\'{image_id}\'''')
            obj = cur.fetchone()
            if obj is None:
                db_disconnect(conn,cur) 
                return make_response(jsonify({'message':'Image not found.'}), 404)
            file = os.path.join(BASE_DIR, f'media\{obj[2]}')
            if os.path.isfile(file):
                os.remove(file)
                cur.execute(f'''DELETE FROM public."Image" WHERE id=\'{image_id}\'''') 
            else:
                return make_response(jsonify({'message':'No such file/image exists.'}),404)
        # commit the changes 
        conn.commit() 
        db_disconnect(conn,cur) 
        return make_response(jsonify({'message':'Images deleted successfully'}),200)
    except Exception as e:
        db_disconnect(conn,cur)
        return make_response(jsonify({'message':'Images not deleted.', 'error': e}),400)
    

if __name__ == '__main__': 
	app.run(debug=True) 
