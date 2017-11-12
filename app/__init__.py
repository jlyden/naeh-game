from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create instance of Flask
app = Flask(__name__)
app.config.from_object('config')

# Set static_url_path to point to node_modules
app.add_url_rule(
    app.static_url_path + '/<path:filename>',
    endpoint='static', view_func=app.send_static_file)
app.url_map
Map([<Rule '/PREFIX/static/<filename>' (HEAD, OPTIONS, GET) -> static>])

# Create instance of SQLAlchemy
db = SQLAlchemy(app)

from app import models, views, utils
