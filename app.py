from flask import Flask, render_template, session, request, redirect, url_for, flash,g
from functools import wraps
import sys
import os
from datetime import datetime
from models import *
from forms import *
from utils import *

# Create a Flask Instance
app = Flask(__name__, template_folder="Templates")

# Secret Key!
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"



users_ = []

usersetup = False
if os.path.isfile('users/tsai.json'):
    usersetup = True
users_.append(User(username="tsai", email="tsai@1234", password="12345",setupComplete=usersetup))



active_user = None
active_username = None
# active_user = users_[0]
# active_username = active_user.username



projects_info = {}

msg_codes = {
    '1':None,
    '2':'Loop Exists',
    '3':'Successfully Saved Project',
    '4':'Error! Project not saved'
}
form_end_indicator = "Default End"
form_start_indicator = "Start"

@app.route("/")
def index():
    return render_template('home.html')     

@app.route("/login", methods=['GET', 'POST'])
def login():

    global active_user
    global active_username

    email = None
    password = None
    form = LoginForm()
    if form.validate_on_submit():

        session.pop('user_id', None)

        email = form.email.data
        password = form.password.data

        # print(email,password, file=sys.stderr)

        form.email.data = ''
        form.password.data = ''
        
        users = [x for x in users_ if email == x.email]
        # print(users, file=sys.stderr)
        if users and password == users[0].password:
            active_user = users[0]
            session['active_username'] = active_user.username
            active_username = active_user.username
            g.user = active_user.username
            projects_info[active_username] = {'projects':{}}
            if active_user.setupComplete:
                return redirect('/projectslist')
            else:
                return redirect('/usersetup')
        else:
            return render_template('login.html', email=email, password=password, form=form, login_success=0)

    return render_template('login.html', email=email, password=password, form=form, login_success=2)


# prevent user from directly going here without logging in

@app.route("/usersetup", methods=['GET', 'POST'])
def UserSetup():

    form = UserSetupForm()
    if form.validate_on_submit() and active_user:
        
        setupComplete=True
        active_user.setup_complete(setupComplete,form.name.data,form.usingFor.data,form.industry.data,form.org.data,form.role.data,form.activity.data,form.howFound.data)

        # print(active_user.org )
        form.name.data = ''
        form.usingFor.data = ''
        form.industry.data = ''
        form.org.data = ''
        form.role.data = ''
        form.activity.data = ''
        form.howFound.data = ''

        return redirect('/')
        
    return render_template('user_setup.html', form=form)




@app.route("/projectslist")
def projectsList():

    global projects_info

    if active_user:
        file_path = f'users/{active_username}_projects.json'
        if os.path.isfile(file_path):
            projects_info = read_json(file_path,active_username)
            projects_exists = True        
            # print(projects_info[active_username]['projects'].keys())
            return render_template('projects_list.html',projects_exists=projects_exists,active_user=active_username,projects = projects_info[active_username]['projects'])
        else:
            projects_exists = False
            return render_template('projects_list.html',projects_exists=projects_exists,active_user=active_username)
    return render_template('projects_list.html')

@app.route("/createproject", methods=['GET', 'POST'])
def CreateProject():
    if request.method == 'POST':
        projects = projects_info[active_username]['projects']
        project_id = int(datetime.now().timestamp())
        project_name = request.form.get('project_name')
        projects[str(project_id)]={'project_name':project_name, 'ordering':{}, 'cards':{}}
        # print('Create project',projects_info)
        return redirect(f'/{active_username}/{project_id}/form/input/{project_id}') 
    return render_template('create_project.html')
    




@app.route('/<username>/<project_id>/form/<form_type>/<question_id>', methods=['GET', 'POST'])
def CreateForm(username,project_id,question_id,form_type):

    # print('Project Info-',projects_info[username]['projects'][project_id])
    cards = projects_info[username]['projects'][project_id]['cards']
    # print(cards)
    msg_id='1'

    if request.method =='GET':
        if question_id in cards:
            return render_template('edit_form.html',username= username,cards=cards,project_id=project_id,question_id=question_id,form_type=form_type, options_list=cards[question_id].options)
        else:
            card = FormCard(question_id,form_type)
            cards[question_id]=card
            return render_template('edit_form.html',username= username,project_id=project_id,cards=cards,question_id=question_id,form_type=form_type, options_list=cards[question_id].options,msg=msg_codes[msg_id])

    elif request.method == 'POST':
        # print("POST data: ",question_id,form_type,request.form.get(f"question_{question_id}"),request.form.get(f"{question_id}"))
        cards[question_id].question = request.form.get(f"question_{question_id}")
        
        if form_type == 'Long_Text':
            cards[question_id].options = [request.form.get(f"{question_id}")]
        elif form_type == 'Multiple_Answers' :
            # pass
            print('Checkbox options',request.form.getlist(f"{question_id}"),type(request.form.getlist(f"{question_id}")))
            cards[question_id].options = request.form.getlist(f"{question_id}")
        
        print('isREquired',request.form.getlist('isRequired'))
        if len(request.form.getlist('isRequired'))==0:
            cards[question_id].required = False
        else:
            cards[question_id].required = True
        
        
        # print(cards[question_id].__dict__)
        
        default_ordering(username,project_id,projects_info)
        msg_id = save_project(projects_info,username,project_id)

        return render_template('edit_form.html',username= username,project_id=project_id,cards=cards,question_id=question_id,form_type=form_type,question = cards[question_id].question, options_list=cards[question_id].options,msg=msg_codes[msg_id])
    
    return render_template('edit_form.html',username= username,project_id=project_id,cards=cards,question_id=question_id,form_type=form_type,msg=msg_codes[msg_id])


@app.route('/<username>/<project_id>/form/<form_type>/<question_id>/addchoices', methods=['GET'])
def addchoices(username,project_id,form_type,question_id):
    print('adding choices')
    cards = projects_info[username]['projects'][project_id]['cards']
    if len(cards[question_id].options)==0:
        # print("len=0")
        cards[question_id].options.extend(["Type your Choice"]*2)
    else:
        cards[question_id].options.extend(["Type your Choice"])
    return redirect('/'+username+'/'+project_id+'/form/'+form_type+'/'+question_id)


@app.route('/<username>/<project_id>/<msg_id>/logic', methods=['GET', 'POST'])
def logic(username,project_id,msg_id):

    curr_project = projects_info[username]['projects'][project_id]

    ordering = {}
    msg=msg_codes[msg_id]
    arr = tuple(projects_info[username]['projects'][project_id]['ordering'].keys())[1:]

    if request.method =='GET':
        
        return render_template('logic.html',username= username, project_id=project_id, project=projects_info[username]['projects'][project_id],msg=msg,form_start_indicator=form_start_indicator,form_end_indicator=form_end_indicator)
    
    elif request.method == 'POST':
        ordering[form_start_indicator] =  request.form.get(form_start_indicator)
        for i in arr:
            ordering[i] = request.form.get(f"{i}")
            print(ordering)
        
        # for i in ordering:
        #     if ordering[i] == form_end_indicator:
        #         print(f'{curr_project["cards"][i].question} -- {ordering[i]}')
        #     elif i==form_start_indicator:
        #         print(f'{i} -- {curr_project["cards"][ordering[i]].question}')
        #     else:
        #         print(f'{curr_project["cards"][i].question} -- {curr_project["cards"][ordering[i]].question}')
        
        loop_exists = check_loop_logic(ordering)
        if loop_exists:
            msg_id = '2'
        else:
            projects_info[username]['projects'][project_id]['ordering'] = ordering
            msg_id = save_project(projects_info,username,project_id)

        return render_template('logic.html',username= username, project_id=project_id, project=projects_info[username]['projects'][project_id], order=arr,msg=msg_codes[msg_id],form_start_indicator=form_start_indicator,form_end_indicator=form_end_indicator)

@app.route('/<username>/<project_id>/<msg_id>/response', methods=['GET', 'POST'])
def form_for_response():
    if request.method =='GET':
        return render_template('form_for_response.html')
