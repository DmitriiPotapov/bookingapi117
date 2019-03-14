from os import getenv
from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from app.src.models import db
from app.api.controller.user import bcrypt
from app.src.routes.api_v1 import api_routes as api_v1_routes
from flask_mail import Mail
from app.api.controller.user import mail

# Flask Activation
app = Flask(__name__)

# Set Configurations
secret_key = getenv('SECRET_KEY')
db_uri = getenv('DATABASE_URL')
sql_track_modification = getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
cors_headers = ['content-type', 'x-client-token']
mail_server = getenv('MAIL_SERVER')
mail_port = getenv('MAIL_PORT')
mail_username = getenv('MAIL_USERNAME')
mail_password = getenv('MAIL_PASSWORD')
mail_sender = getenv('MAIL_DEFAULT_SENDER')

# Activate Configurations
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = sql_track_modification
app.config['MAIL_SERVER'] = mail_server
app.config['MAIL_PORT'] = mail_port
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAIL_DEFAULT_SENDER'] = mail_sender

# Activate Extensions
mail.init_app(app)
db.init_app(app)
migrate = Migrate(app, db)
bcrypt.init_app(app)
cors = CORS(app, allow_headers='*', expose_headers='*')

# Main Routes
app.register_blueprint(api_v1_routes)

@app.route('/')
def index():
    return redirect(url_for('documentation_version1'))

@app.route('/api/v1/documentation')
def documentation_version1():
    pass

if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run()