from flask import Flask, render_template, session, request, redirect, url_for, flash,g
from functools import wraps
import sys
import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from datetime import datetime
from models import *
from forms import *
from utils import *
from flask import send_file

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, widgets
from wtforms.validators import Length

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# Create a Flask Instance
app = Flask(__name__, template_folder="Templates",static_url_path='', static_folder='static')

# Secret Key!
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
app.config['MAX_CONTENT_LENGTH'] = 5 * 1000 * 1000  # 5MB


users_ = []

usersetup = False

# root_path = '/home/shilpa/mysite/users/'
# img_folder = '/home/shilpa/mysite/static/images/'

root_path = 'users/'
img_folder = 'static/images/'


save_folder = root_path

with open(root_path+'tsai.json') as json_file:
    usersetup = json.load(json_file)['tsai']['setupComplete']

users_.append(User(username="tsai", email="tsai@1234", password="12345",setupComplete=usersetup))



active_user = None
active_username = None
# active_user = users_[0]
# active_username = active_user.username



projects_info = {}

responses = {}

msg_codes = {
    '1':None,
    '2':'Loop Exists',
    '3':'Successfully Saved Project',
    '4':'Error! Project not saved',
    '5':'Thank You! Form has be submitted.',
    '6':"Error in uploading file! File does not follow the below instructions.",
    '7':"File Size Exceeded limit of 5MB"
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
    global projects_info
    global responses

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
            file_path = f'{root_path}{active_username}_projects.json'

            if os.path.isfile(file_path):
                projects_info = read_json(file_path,active_username)
            else:
                projects_info[active_username] = {'projects':{}}
            file_path = f'{root_path}{active_username}_responsed.json'
            if os.path.isfile(file_path):
                responses = read_response_json(file_path,active_username)

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
        if projects_info[active_username]['projects'] :
            projects_exists = True
            # print('projects---------------- ',projects_info[active_username]['projects'].keys())
            return render_template('projects_list.html',projects_exists=projects_exists,active_user=active_username,projects = projects_info[active_username]['projects'])
        else:
            projects_exists = False
            return render_template('projects_list.html',projects_exists=projects_exists,active_user=active_username)
    return render_template('projects_list.html')

@app.route("/createproject", methods=['GET', 'POST'])
def CreateProject():
    form = CreateProjectForm()
    if request.method == 'POST' and form.validate_on_submit() :
        projects = projects_info[active_username]['projects']
        project_id = int(datetime.now().timestamp())
        project_name = form.project_name.data
        if form.project_time.data:
            total_time = int(form.project_time.data)
        else:
            total_time = 0
        projects[str(project_id)]={'project_name':project_name,"total_time":total_time, 'ordering':{}, 'cards':{}}
        # print('Create project',projects_info)
        return redirect(f'/{active_username}/{project_id}/form/Long_Text/{project_id}')
    return render_template('create_project.html',form=form)




# there might be a problem if user goes directly to this url. project_info variable will be empty

@app.route('/<username>/<project_id>/form/<form_type>/<question_id>', methods=['GET', 'POST'])
def CreateForm(username,project_id,question_id,form_type):

    global projects_info

    # print('Project Info-',projects_info[username]['projects'][project_id])
    cards = projects_info[username]['projects'][project_id]['cards']
    # print(cards)
    msg_id='1'


    if request.method =='GET':
        if question_id in cards:
            return render_template('edit_form.html',project_name=projects_info[username]['projects'][project_id]["project_name"],username= username,cards=cards,project_id=project_id,question_id=question_id,form_type=form_type, options_list=cards[question_id].options)
        else:
            card = FormCard(question_id,form_type)
            cards[question_id]=card
            return render_template('edit_form.html',project_name=projects_info[username]['projects'][project_id]["project_name"],username= username,project_id=project_id,cards=cards,question_id=question_id,form_type=form_type, options_list=cards[question_id].options,msg=msg_codes[msg_id])

    elif request.method == 'POST':
        # print("POST data: ",question_id,form_type,request.form.get(f"question_{question_id}"),request.form.get(f"{question_id}"))
        cards[question_id].question = request.form.get(f"question_{question_id}")

        if form_type == 'Long_Text':
            cards[question_id].options = [request.form.get(f"{question_id}")]
        elif form_type == 'Multiple_Answers' :
            # pass
            # print('Checkbox options',request.form.getlist(f"{question_id}"),type(request.form.getlist(f"{question_id}")))
            cards[question_id].options = request.form.getlist(f"{question_id}")

        # print('isREquired',request.form.getlist('isRequired'))
        if len(request.form.getlist('isRequired'))==0:
            cards[question_id].required = False
        else:
            cards[question_id].required = True


        # print(cards[question_id].__dict__)

        projects_info = default_ordering(username,project_id,projects_info)
        msg_id = save_project(projects_info,username,project_id)

        return render_template('edit_form.html',project_name=projects_info[username]['projects'][project_id]["project_name"],username= username,project_id=project_id,cards=cards,question_id=question_id,form_type=form_type,question = cards[question_id].question, options_list=cards[question_id].options,msg=msg_codes[msg_id])

    return render_template('edit_form.html',project_name=projects_info[username]['projects'][project_id]["project_name"],username= username,project_id=project_id,cards=cards,question_id=question_id,form_type=form_type,msg=msg_codes[msg_id])


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

    # curr_project = projects_info[username]['projects'][project_id]

    ordering = {}
    msg=msg_codes[msg_id]
    arr = tuple(projects_info[username]['projects'][project_id]['ordering'].keys())[1:]

    if request.method =='GET':

        return render_template('logic.html',username= username, project_id=project_id, project=projects_info[username]['projects'][project_id],msg=msg,form_start_indicator=form_start_indicator,form_end_indicator=form_end_indicator)

    elif request.method == 'POST':
        ordering[form_start_indicator] =  request.form.get(form_start_indicator)
        for i in arr:
            ordering[i] = request.form.get(f"{i}")
            # print(ordering)

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


# form class with static fields
def get_Form():
    class MyForm(FlaskForm):
        blah = StringField('blah')
    return MyForm

def parse_form(file_path,username,project_id):
    with open(file_path) as json_file:
        d = json.load(json_file)
    # print(d)
    dictionary = d[username]['projects'][project_id]
    formclass = get_Form()

    num_cards = len(dictionary['ordering'])

    for i in range(num_cards-1):
        if i==0:
            card = dictionary['ordering']['Start']
        else:
            card = dictionary['ordering'][card]

        if dictionary['cards'][card]['answer_type']=='Long_Text':
            if dictionary['cards'][card]['required'] == True:
                setattr(formclass, dictionary['cards'][card]['id'], StringField(dictionary['cards'][card]['question'],validators=[DataRequired(),Length(min=50,max=500)]))
            else:
                setattr(formclass, dictionary['cards'][card]['id'], StringField(dictionary['cards'][card]['question'],validators=[Length(min=50,max=500)]))
        if dictionary['cards'][card]['answer_type']=='Short_Text':
            if dictionary['cards'][card]['required'] == True:
                setattr(formclass, dictionary['cards'][card]['id'], StringField(dictionary['cards'][card]['question'],validators=[DataRequired(),Length(min=10,max=144)]))
            else:
                setattr(formclass, dictionary['cards'][card]['id'], StringField(dictionary['cards'][card]['question'],validators=[Length(min=10,max=144)]))
        if dictionary['cards'][card]['answer_type']=='Multiple_Answers':
            choice = []
            for op in  dictionary['cards'][card]['options']:
                choice.append((op,)*2)
            # print(choice,type(choice))
            if dictionary['cards'][card]['required'] == True:
                setattr(formclass, dictionary['cards'][card]['id'], MultiCheckboxField(dictionary['cards'][card]['question'], choices=choice, validators=[DataRequired()]))
            else:
                setattr(formclass, dictionary['cards'][card]['id'], MultiCheckboxField(dictionary['cards'][card]['question'], choices=choice))

    setattr(formclass,"submit", SubmitField("Submit"))
    form = formclass(request.form)
    return form ,dictionary

# http://127.0.0.1:5000/tsai/1631357726/response
@app.route('/<username>/<project_id>/<msg_id>/response', methods=['GET', 'POST'])
def form_for_response(username,project_id,msg_id):
    file_path =root_path+username + '_projects.json'
    form,project_dict = parse_form(file_path,username,project_id)
    
    if request.method =='GET':
        return render_template('form_for_response.html',form=form,msg=msg_codes[msg_id],username=username,project_id=project_id)
    elif form.validate_on_submit():
        respose_data = {}
        for i in project_dict['cards'].keys():
                if isinstance(form[i].data, list):
                    respose_data[i] = form[i].data
                else:
                    respose_data[i] = [form[i].data]
        respose_data['Date'] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        response_id = int(datetime.now().timestamp())

        file_path = f'{root_path}{username}_responsed.json'
        if os.path.isfile(file_path):
            response = read_response_json(file_path,username)
        else:
            response = {username:{project_id:{}}}

        response[username][project_id][response_id] = respose_data
        write_to_json(response,file_path)

        return render_template('form_for_response.html',form=form,msg=msg_codes['5'],username=username,project_id=project_id)


@app.route('/<username>/<project_id>/responseslist',methods=['GET'])
def responseslist(username,project_id):
    responses_list = {}
    # print('responses :',responses)
    if responses:
        if responses[username][project_id] :
            responses_list = responses[username][project_id]

    # print(projects_info[username]['projects'][project_id])
    return render_template('response_list.html',responses_list=responses_list,project_name=projects_info[username]['projects'][project_id]["project_name"],project_id=project_id,username=username)

@app.route('/<username>/<project_id>/showresponses/<response_id>',methods=['GET'])
def showresponses(username,project_id,response_id):
    curr_response = responses[username][project_id][response_id]
    curr_project = projects_info[username]['projects'][project_id]

    return render_template("show_response.html",curr_project=curr_project,curr_response=curr_response)


@app.route('/<username>/importform',methods=['GET','POST'])
def importform(username):
    global projects_info
    form = UploadForm()

    if request.method =='GET':
        return render_template('import_form.html',username=username,form=form,msg=msg_codes['1'])


    if form.validate_on_submit():

        filename = secure_filename(form.upload.data.filename)
        # print(filename)
        form.upload.data.save(root_path + filename)
        res = excel_to_json(username, filename)
        if res:
            file_path = f'{root_path}{active_username}_projects.json'


            projects_info = read_json(file_path,active_username)
            return redirect('/')
        else:
            return render_template('import_form.html',username=username,form=form,msg=msg_codes['6'],img_folder=img_folder)
    else:
        return render_template('import_form.html',username=username,form=form,msg=msg_codes['6'],img_folder=img_folder)

def downloadable_project_file(username,projects_info,project_id):
    curr_project = projects_info[username]['projects'][project_id]
    df = pd.DataFrame()
  
    cols = ['question', 'options', 'answer_type', 'answers', 'score', 'required']
    for i in curr_project['cards']:
        card = curr_project['cards'][i]
        
        tmp = pd.DataFrame([[card.question,str(card.options).replace("'",""),card.answer_type,str(card.answers).replace("'",""),card.score,card.required]],columns = cols )
        df = df.append(tmp)
    df['project_name'] = np.nan
    df['project_name'].iloc[0] = curr_project['project_name']
    df['total_time(project)'] = np.nan
    df['total_time(project)'].iloc[0] = curr_project['total_time']
    df = df[['project_name','total_time(project)','question', 'options', 'answer_type', 'answers', 'score', 'required']]
    df.to_csv(f'{save_folder}{username}_form_download.csv',index=False)
    return f'{save_folder}{username}_form_download.csv'

@app.route('/<username>/<project_id>/download')
def downloadprojectfile(username,project_id):
    file_path = downloadable_project_file(username,projects_info,project_id)
    return send_file(file_path, as_attachment=True)

