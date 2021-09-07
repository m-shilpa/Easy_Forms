from functools import wraps
from flask import g, request, redirect, url_for
from models import *





# details -  https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print('in decorator')
        if active_username is None:
            print('no user')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function