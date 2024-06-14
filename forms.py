from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length


class GetCode(FlaskForm):
    code = StringField('code', validators=[InputRequired(), Length(min=5)])
    two_code = StringField('2facode')


class Login(FlaskForm):
    username = StringField('phone', validators=[InputRequired(), Length(min=4)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4)])
    remember_me = BooleanField('remember_me')


class EditProfile(FlaskForm):
    password = PasswordField('password', validators=[Length(min=5)])
    twofacode = PasswordField('2facode', validators=[Length(min=2)])