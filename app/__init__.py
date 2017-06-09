from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create instance of Flask
app = Flask(__name__)
app.config.from_object('config')

# Create instance of SQLAlchemy
db = SQLAlchemy(app)

from app import views, models
