from flask import Flask, render_template, session, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, validators
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
import sys

from models import *


# Create a Flask Instance
app = Flask(__name__, template_folder="Templates")

# Secret Key!
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
# logging.basicConfig(level=logging.DEBUG)

users = []
users.append(User(id=1, email="tsai@1234", password="12345"))


class UserSetupForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    email = EmailField("Email address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route("/")
def index():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    email = None
    password = None
    form = LoginForm()
    if form.validate_on_submit():

        session.pop('user_id', None)

        email = form.email.data
        password = form.password.data

        print(email,password, file=sys.stderr)

        form.email.data = ''
        form.password.data = ''
        
        user = [x for x in users if email == x.email][0]
        print(user, file=sys.stderr)
        if user and password == user.password:
            session['user_id'] = user.id
            return redirect('/')
        else:
            return render_template('login.html', email=email, password=password, form=form, login_succes=0)

    return render_template('login.html', email=email, password=password, form=form, login_success=2)



@app.route("/UserSetup", methods=['GET', 'POST'])
def UserSetup():
    name = None
    form = UserSetupForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        # return redirect(url_for('/'))
        return render_template('user_setup.html', name=name, form=form)
    return render_template('user_setup.html', name=name, form=form)