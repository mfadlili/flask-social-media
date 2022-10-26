from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired

class ChatUser(FlaskForm):
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')
