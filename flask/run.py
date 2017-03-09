#!/usr/bin/python3

from app import app
app.run(host='0.0.0.0', debug=True)

# def connect():
#     connection = sqlalchemy.create_engine(config.SQLALCHEMY_DATABASE_URI,
#                                           client_encoding='utf8')
#     metadata = sqlalchemy.MetaData(bind=connection, reflect=True)
#     return connection, metadata
