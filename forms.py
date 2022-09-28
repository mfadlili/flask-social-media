from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf.file import FileField,FileAllowed
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    login = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    email = StringField('Email: ', validators=[DataRequired(), Email()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password: ', validators=[DataRequired(), EqualTo('password')])
    register = SubmitField('Register')

    def check_username(self, username):
        if User.query.filter_by(username = username.data).first():
            raise ValidationError('The username already taken')
    
    def check_email(self, email):
        if User.query.filter_by(email = email.data).first():
            raise ValidationError('The email already taken')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Contents', validators=[DataRequired()])
    post = SubmitField('Post')

class EditProfile(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    about = TextAreaField('About', validators=[DataRequired()])
    photo = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfile, self).__init__(*args, **kwargs)
        self.original_username =  original_username

    def check_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username = username.data).first()
            if user is not None:
                raise ValidationError('The username already taken')
    
    def check_email(self, email):
        if User.query.filter_by(email = email.data).first():
            raise ValidationError('The email already taken')  

class EditPost(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Contents', validators=[DataRequired()])
    post = SubmitField('Update')

class AddComment(FlaskForm):
    body = TextAreaField('Contents', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ChatUser(FlaskForm):
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

