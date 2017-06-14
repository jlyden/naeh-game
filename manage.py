#!/usr/bin/python3
#
# To initialize migration support: .\manage.py db init
# To generate a migration: .\manage.py db migrate
# To apply the migration: .\manage.py db upgrade
# If NameError, add "sa." before terms lacking it
# From https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db


app.config.from_object('config')

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
