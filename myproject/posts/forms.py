from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Contents', validators=[DataRequired()])
    post = SubmitField('Post')
 
class EditPost(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Contents', validators=[DataRequired()])
    post = SubmitField('Update')

class AddComment(FlaskForm):
    body = TextAreaField('Contents', validators=[DataRequired()])
    submit = SubmitField('Submit')