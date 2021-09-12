from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, validators,RadioField,IntegerField
from wtforms.validators import DataRequired, Regexp
from wtforms.fields.html5 import EmailField

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired

class SignUpForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired(), Regexp('^\w+$',message="Username must contain only letters numbers or underscore")])
    email = EmailField("Email address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class CreateProjectForm(FlaskForm):
    project_name= StringField("Project Name", validators=[DataRequired()])
    project_time = IntegerField("Total Time in minutes ( min=0 and max=180 minutes)", validators=[
                validators.NumberRange(min=1, max=180,message="Please enter a number in from 1 to 180 "),validators.Optional()
            ])
    submit = SubmitField("Submit")

class UserSetupForm(FlaskForm):

    app_name = "Easy Forms"

    name = StringField("What is your Name ?", validators=[DataRequired()])
    usingFor_choices = ("Work","School","Personal")

    usingFor = RadioField(f"What is the one thing you'll be using {app_name} for ?", choices=usingFor_choices, default='value_two')

    industry_choices = ("Health Care","E-Commerce","Consumer Serivces","Professional Services","Other")
    industry = RadioField(f"What industry are you in ?", choices = industry_choices, validators = [DataRequired()])

    org_choices = ("2-10","10-100","100-1000","1000+")
    org = RadioField(u"What Size is your Organization ?", choices = org_choices, validators = [DataRequired()])

    role_choices = ("Marketing","Sales","Founder/CEO","Human Resources","Other")
    role = RadioField(f"Which of these best describes your role ?", choices = role_choices, validators = [DataRequired()])

    activity_choices = ("Conduct research","Manage feedback","Manage events,projects or requests", "Accept payments")
    activity = RadioField(f"What is the one main activity you want to do with {app_name}", choices = activity_choices, validators = [DataRequired()])

    howFound_choices = ("Newsletter","Youtube",f"Filling in someone else's {app_name}","Article,link or website")
    howFound = RadioField(f"How did you first discover {app_name}", choices = howFound_choices, validators = [DataRequired()])

    submit = SubmitField("Let's start")


class LoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# def FileSizeLimit(max_size_in_mb):
#     max_bytes = max_size_in_mb*1024*1024
#     def file_length_check(form, field):
#         if len(field.data.read()) > max_bytes:
#             raise ValidationError(f"File size must be less than {max_size_in_mb}MB")
    
#     return file_length_check

class UploadForm(FlaskForm):
    upload = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'csv Files only!')
    ])