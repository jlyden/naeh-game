#!/usr/bin/python3

import os
import unittest

from app import app, db
from app.models import Game, Emergency, Rapid, Transitional, Permanent


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            'postgresql+psycopg2://flask:Flask@localhost/test'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


if __name__ == '__main__':
    unittest.main()
