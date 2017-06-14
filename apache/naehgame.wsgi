#!/usr/bin/python

import sys
import logging

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0,"/var/www/naehgame/")

from naehgame import app as application
app.config.from_object('config')
