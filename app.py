from flask import Flask, render_template, session, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, validators
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField



# Create a Flask Instance
app = Flask(__name__)

# Secret Key!
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
# logging.basicConfig(level=logging.DEBUG)


class NamerForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    # email = EmailField("Email address", validators=[DataRequired()])
    # password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route("/")
def index():
    return render_template('home.html')

@app.route("/UserSetup", methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        # return redirect(url_for('/'))
        return render_template('user_setup.html', name=name, form=form)
    return render_template('user_setup.html', name=name, form=form)