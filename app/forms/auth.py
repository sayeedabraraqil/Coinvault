import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    identity = StringField('Username or Email', validators=[
        DataRequired(message='Enter your username or email address.')
    ], render_kw={"placeholder": "e.g. striker99 or user@domain.com"})
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ], render_kw={"placeholder": "••••••••••••"})
    remember_me = BooleanField('Keep terminal session active')
    submit = SubmitField('Access Terminal')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username is required.'),
        Length(min=3, max=32, message='Username must be between 3 and 32 characters.')
    ], render_kw={"placeholder": "e.g. apex_striker"})
    
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please provide a valid email format.')
    ], render_kw={"placeholder": "name@example.com"})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=8, message='Password must be at least 8 characters long.')
    ], render_kw={"placeholder": "Minimum 8 characters"})
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ], render_kw={"placeholder": "Repeat password"})
    
    submit = SubmitField('Create Terminal Account')

    def validate_username(self, field):
        if not re.match(r'^[a-zA-Z0-9_-]+$', field.data):
            raise ValidationError('Username can only contain alphanumeric characters, underscores, and dashes.')
        existing = User.query.filter_by(username=field.data.lower()).first()
        if existing:
            raise ValidationError('This handle is already registered in the vault.')

    def validate_email(self, field):
        existing = User.query.filter_by(email=field.data.lower()).first()
        if existing:
            raise ValidationError('An account with this email address already exists.')


class RequestResetForm(FlaskForm):
    email = StringField('Registered Email', validators=[
        DataRequired(),
        Email()
    ], render_kw={"placeholder": "your-account@domain.com"})
    submit = SubmitField('Send Password Reset Link')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Update Password')
