from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from werkzeug.utils import secure_filename
import numpy as np
import os


model = load_model('20210515-19291621106993-89Percent.h5')

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Testing@3122'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webapp.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/')
def default():
    return render_template('login.html')

@app.route('/login_user', methods=['POST'])
def login():
    username= request.form['user-name']
    password= request.form['password']
    print(username)
    print(password)
    user = Users.query.filter_by(username=username, password=password).first()

    if not user:
        return '<h1> User not found!</h1>'

    login_user(user)

    return render_template('index.html')

@login_required
@app.route('/index')
def index():
    return render_template('index.html')

@login_required
@app.route('/dataview')
def dataview():
    return render_template('dataview.html')

def model_predict(file_path, model):
    img = image.load_img(file_path, target_size=(299,299))

    x = image.img_to_array(img)

    x = np.expand_dims(x, axis=0)

    x = preprocess_input(x, mode='caffe')

    predictions = model.predict(x)
    return predictions

def convert_prediction(prediction):
    if prediction >= 0.5:
        return "NORMAL"
    else:
        return "COVID"

@app.route('/predict', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        # get file
        file = request.files['file']

        # save file to uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'uploads', secure_filename(file.filename))
        file.save(file_path)

        #Make prediction
        prediction = model_predict(file_path, model)
        print(prediction[0])

        return convert_prediction(prediction[0])
    return None
    
if __name__ == "__main__":
    app.run(debug=True)

