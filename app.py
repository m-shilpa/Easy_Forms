from flask import Flask, render_template, session, request, redirect, url_for, flash
import sys
import os
from models import *
from forms import *
from datetime import datetime

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

@app.route("/")
def index():
    return render_template('home.html')

# @app.route("/SignUp",methods=['GET','POSt'])
# def signup():
#     username = None
#     email = None
#     password = None 
#     form = SignUpForm()
    
#     if form.validate_on_submit():
#         if os.path.isfile(form.username.data+'.json') == False:
#             user = User(username=username, email=form.email.data, password=form.password.data)
#             return redirect('/Login')
#         else:
#             return render_template('signup.html', form=form, msg="UserName already exists! Please try different username")

#     return render_template('signup.html', form=form, msg=None)
        

@app.route("/Login", methods=['GET', 'POST'])
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

        print(email,password, file=sys.stderr)

        form.email.data = ''
        form.password.data = ''
        
        users = [x for x in users_ if email == x.email]
        print(users, file=sys.stderr)
        if users and password == users[0].password:
            active_user = users[0]
            session['active_username'] = active_user.username
            active_username = active_user.username
            projects_info[active_username] = {'projects':{}}
            if active_user.setupComplete:
                return redirect('/ProjectsList')
            else:
                return redirect('/UserSetup')
        else:
            return render_template('login.html', email=email, password=password, form=form, login_success=0)

    return render_template('login.html', email=email, password=password, form=form, login_success=2)


# prevent user from directly going here without logging in

@app.route("/UserSetup", methods=['GET', 'POST'])
def UserSetup():

    form = UserSetupForm()
    if form.validate_on_submit() and active_user:
        
        setupComplete=True
        active_user.setup_complete(setupComplete,form.name.data,form.usingFor.data,form.industry.data,form.org.data,form.role.data,form.activity.data,form.howFound.data)

        print(active_user.org )
        form.name.data = ''
        form.usingFor.data = ''
        form.industry.data = ''
        form.org.data = ''
        form.role.data = ''
        form.activity.data = ''
        form.howFound.data = ''

        return redirect('/')
        
    return render_template('user_setup.html', form=form)






# @app.route('/background_process_test/<form_type>')
# def background_process_test(form_type):
#     print (form_type)
#     types.append(form_type)
#     print(types)
    
#     now = datetime.now().strftime('%Y%m%d%H%M%S')
#     question_ids.append(now)

#     return redirect(f'/form/{now}/{form_type}')

# @app.route("/sample")
# def sample():
#     return render_template('sample.html',cards=types)




@app.route("/ProjectsList")
def projectsList():

    global projects_info

    if active_user:
        file_path = f'users/{active_username}_projects.json'
        if os.path.isfile(file_path):
            projects_info = read_json(file_path,active_username)
            projects_exists = True        
    
            return render_template('projects_list.html',projects_exists=projects_exists,active_user=active_username,projects = projects_info[active_username]['projects'])
        else:
            projects_exists = False
            return render_template('projects_list.html',projects_exists=projects_exists,active_user=active_username)
    return render_template('projects_list.html')

@app.route("/CreateProject", methods=['GET', 'POST'])
def CreateProject():
    if request.method == 'POST':
        projects = projects_info[active_username]['projects']
        project_id = int(datetime.now().timestamp())
        project_name = request.form.get('project_name')
        projects[str(project_id)]={'project_name':project_name, 'cards':{}}
        print('Create project',projects_info)
        return redirect(f'/{active_username}/{project_id}/form/input/{project_id}') 
    return render_template('create_project.html')
    

@app.route('/<username>/<project_id>/form/<form_type>/<question_id>', methods=['GET', 'POST'])
def CreateForm(username,project_id,question_id,form_type):

    # print('Project Info-',projects_info[username]['projects'][project_id])
    cards = projects_info[username]['projects'][project_id]['cards']
    # print(cards)

    if request.method =='GET':
        if question_id in cards:
            return render_template('edit_form.html',username= username,cards=cards,project_id=project_id,question_id=question_id,form_type=form_type, options_list=cards[question_id].options)
        else:
            card = FormCard(question_id,form_type)
            cards[question_id]=card
            return render_template('edit_form.html',username= username,project_id=project_id,cards=cards,question_id=question_id,form_type=form_type, options_list=cards[question_id].options)

    elif request.method == 'POST':
        # print("POST data: ",question_id,form_type,request.form.get(f"question_{question_id}"),request.form.get(f"{question_id}"))
        cards[question_id].question = request.form.get(f"question_{question_id}")
        cards[question_id].position = len(cards)
        if form_type == 'input':
            cards[question_id].options = [request.form.get(f"{question_id}")]
        elif form_type == 'checkbox' :
            # pass
            print('Checkbox options',request.form.getlist(f"{question_id}"),type(request.form.getlist(f"{question_id}")))
            cards[question_id].options = request.form.getlist(f"{question_id}")
        
        
        # print(cards[question_id].__dict__)

        return render_template('edit_form.html',username= username,project_id=project_id,cards=cards,question_id=question_id,form_type=form_type,question = cards[question_id].question, options_list=cards[question_id].options)
    
    return render_template('edit_form.html',username= username,project_id=project_id,cards=cards,question_id=question_id,form_type=form_type)

@app.route('/<username>/<project_id>/form/<form_type>/<question_id>/saveproject', methods=['GET'])
def saveproject(username,project_id,form_type,question_id):
    res = save_project_to_json(projects_info,username,project_id)
    print(res)
    if res:
        flash('Successfully saved project')
    else:
        flash('Something went wrong. Project not saved.')
    return redirect('/'+username+'/'+project_id+'/form/'+form_type+'/'+question_id)

@app.route('/<username>/<project_id>/form/<form_type>/<question_id>/addchoices', methods=['GET'])
def addchoices(username,project_id,form_type,question_id):
    print('adding choices')
    cards = projects_info[username]['projects'][project_id]['cards']
    cards[question_id].options.extend(["Type your Choice"])
    return redirect('/'+username+'/'+project_id+'/form/'+form_type+'/'+question_id)

