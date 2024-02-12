from flask_wtf import FlaskForm

# Predictions Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SelectField, SelectMultipleField

# Login Form
from wtforms import StringField, BooleanField, EmailField, PasswordField, SubmitField
from wtforms.validators import Length, InputRequired, ValidationError, NumberRange, EqualTo
from application.models import User

# Prediction Form
vegetables = [
    ('Bean', 'Bean'), 
    ('Bitter Gourd', 'Bitter Gourd'), 
    ('Bottle Gourd', 'Bottle Gourd'), 
    ('Brinjal', 'Brinjal'), 
    ('Broccoli', 'Broccoli'), 
    ('Cabbage', 'Cabbage'), 
    ('Capsicum', 'Capsicum'),
    ('Carrot', 'Carrot'), 
    ('Cauliflower', 'Cauliflower'), 
    ('Cucumber', 'Cucumber'),
    ('Papaya', 'Papaya'),
    ('Potato', 'Potato'),
    ('Pumpkin', 'Pumpkin'),
    ('Radish', 'Radish'),
    ('Tomato', 'Tomato')
]

models = [
    ('31x31', '31x31'),
    ('128x128', '128x128')
]

class PredictionForm(FlaskForm):
    imageInput = FileField('Select image', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    model = SelectField('Select Model', choices=models, validators=[InputRequired()])
    submit = SubmitField('Predict')

# User Sign Up Form
class UserSignUpForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={'placeholder': 'JohnDoe'})
    email = EmailField('Email', validators=[InputRequired()], render_kw={'placeholder': 'johndoe@gmail.com'})
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirmPassword', message='Passwords must match'), Length(min=12, max=80)], render_kw={'placeholder': '********'})
    confirmPassword = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')], render_kw={'placeholder': '********'})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        # Make sure username does not contain spaces
        if ' ' in username.data:
            raise ValidationError('Username cannot contain spaces!')
        # Make sure no special characters in username
        elif not username.data.isalnum():
            raise ValidationError('Username can only contain letters and numbers!')

    def validate_email(self, email):
        # Check if email already exists
        existing_email = User.query.filter_by(email=email.data).first()

        if existing_email:
            raise ValidationError('Email already exists!')
        
# Filter Form
pastDaysChoices = [
    ('None', 'All'),
    ('1 hours', 'Last hour'),
    ('1 days', 'Last day'),
    ('7 days', 'Last week'),
    ('31 days', 'Last month'),
    ('365 days', 'Last year'),
]

models = [
    ('None', 'All'),
    ('31x31', '31x31'),
    ('128x128', '128x128')
]

class FilterPredForm(FlaskForm):
    pastDays = SelectField('', choices=pastDaysChoices)
    modelFilter = SelectField('', choices=models)
    vegetableFilter = SelectMultipleField('', choices=vegetables)
    searchFilter = StringField('')
        
# User Login Form
class UserLoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()], render_kw={'placeholder': 'JohnDoe@gmail.com'})
    remember = BooleanField('Remember Me?', default=False)
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

# User Change username
class UserChangeUsernameForm(FlaskForm):
    username = StringField('New Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={'placeholder': 'JohnDoe'})
    submit = SubmitField('Change Username')

    def validate_username(self, username):
        # Make sure username does not contain spaces
        if ' ' in username.data:
            raise ValidationError('Username cannot contain spaces!')
        # Make sure no special characters in username
        elif not username.data.isalnum():
            raise ValidationError('Username can only contain letters and numbers!')
        
# User Change password
class UserChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirmPassword', message='Passwords must match'), Length(min=12, max=80)], render_kw={'placeholder': '********'})
    confirmPassword = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')], render_kw={'placeholder': '********'})
    submit = SubmitField('Change Password')

# User Delete account
class UserDeleteAccForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={'placeholder': 'JohnDoe'})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=12, max=80)], render_kw={'placeholder': '********'})
    delete = SubmitField("Yes, I'm Sure")
    
