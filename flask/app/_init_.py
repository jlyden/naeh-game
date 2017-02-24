from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Create instance of Flask
app = Flask(__name__)
app.config.from_object('config')
app.secret_key = 'jkl_jkl_asd_asd'

# Create instance of SQLAlchemy
db = SQLAlchemy(app)

from app import views, models
