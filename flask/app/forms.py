from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class NewGameForm(Form):
    team_name = StringField('team_name', validators=[DataRequired()])
