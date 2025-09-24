from flask import Flask, request, jsonify, make_response, render_template
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

BASE_DIR = app.root_path

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'media')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True,)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    image_type = db.Column(db.String(15), nullable=False)
    sequence_no = db.Column(db.Integer, default=1)

    def __init__(self, name, image, image_type, sequence_no):
        self.name = name
        self.image = image
        self.image_type = image_type
        self.sequence_no = sequence_no

@app.route('/', methods=['GET'])
def index():
    return "You are not supposed to be here.<br/><br/>If any queries, kindly mail to: pavankumarmaurya1999@gmail.com."


@app.route('/get', methods=['GET'])
def get():
    images = Image.query.all()
    print(images)
    return render_template('images.html', images=images)

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
                cnt=Image.query.filter_by(image_type=image_type).count() + 1
                for file in images:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        # Save the files
                        try:
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            image = Image(name, filename, image_type, cnt)
                            db.session.add(image)
                            db.session.commit()
                            cnt+=1
                        except Exception as e:
                            return f'Error saving file: {str(e)}', 500
                    elif not allowed_file(file.filename):
                        return make_response(jsonify({'message':'File type not allowed.'}), 400)
                return make_response(jsonify({'message':'Images uploaded successfully'}),200)
            else:
                return make_response(jsonify({'message': 'No images found in the request.'}), 400)
        except Exception as e:
            return make_response(jsonify({'message': 'Images upload failed.','error': e}), 400)

@app.route('/delete', methods=['POST']) 
def delete(): 
    try:
        images_to_delete = request.form['images_to_delete']
        images_to_delete = images_to_delete.split(",")
        for image_id in images_to_delete:
            # Delete the data from the table
            obj = Image.query.filter_by(id=image_id).first()
            if obj is None:
                return make_response(jsonify({'message':'Image not found.'}), 404)
            file = os.path.join(BASE_DIR, f'media\{obj.__dict__["image"]}')
            if os.path.isfile(file):
                os.remove(file)
                db.session.delete(obj)
            else:
                db.session.delete(obj)
                return make_response(jsonify({'message':'No such file/image exists.'}),404)
            db.session.commit() 
        return make_response(jsonify({'message':'Images deleted successfully'}),200)
    except Exception as e:
        return make_response(jsonify({'message':'Images not deleted.', 'error': e}),400)
    

if __name__ == '__main__': 
	app.run(debug=True) 
