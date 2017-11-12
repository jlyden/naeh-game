#!/usr/bin/python3
#
# To initialize migration support: ./manage.py db init
# To generate a migration: ./manage.py db migrate
# To apply the migration: ./manage.py db upgrade

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db


app.config.from_object('config')

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
