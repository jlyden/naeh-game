import os
basedir = os.path.abspath(os.path.dirname(__file__))

# is this URI really right?
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://flask:FlasK@localhost:5432/flask'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True
SECRET_KEY = '4$3cr3t4'
