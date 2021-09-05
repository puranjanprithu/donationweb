from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SECRET_KEY']='4a71bc10b0527757ec171e1f'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

app.config['IMAGE_UPLOADS']="D:\\projects\\websites\\github\\Donation\\market\\static\\img\\uploads"
app.config['ALLOWED_IMAGE_EXTENSIONS']=['PNG','JPEG','JPG','GIF']
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'eazyprints180@gmail.com'
app.config['MAIL_PASSWORD'] = 'Eazyprints@2020'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


bcrypt= Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_view="login_page"
login_manager.login_message_category="info"
from market import routes


