import json
import copy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, validators,RadioField,SelectMultipleField
from wtforms.validators import DataRequired, Regexp
from wtforms.fields.html5 import EmailField
from wtforms.widgets import CheckboxInput,ListWidget
import pandas as pd
import random 
from datetime import datetime
import numpy as np
import os

def excel_to_json(username, file_name):
    file_path = 'users/' + file_name
    df = pd.read_csv(file_path)
    print(df.shape)
    print(df)
    df.columns= df.columns.str.strip().str.lower()
    cols = ['question', 'options', 'answer_type', 'answers', 'score', 'required']
    for i in cols:
        if i not in df.columns:
            return False
    df = df[['question', 'options', 'answer_type', 'answers', 'score', 'required']]
    # if anser_type contians return failed

    if df['answer_type'].isnull().values.any():
        return False
    
    df['question'] = df['question'].fillna("")

    df['options'] = df['options'].str.replace('[','',1)
    df['options'] = df['options'].str.replace(']','',1)
    df['options'] = df['options'].str.split(',')
    isna = df['options'].isna()
    df.loc[isna, 'options'] = pd.Series([[]] * isna.sum()).values
    

    # validate if options match the answer type. Also check length of options shouldn't be greater than a threshold

    # fill required with True
    df['required'] = df['required'].fillna(True)

    # check if there are any other values other name True , False
    
    df =df.replace({np.nan: None})

    d = df.to_dict('records')
    n1 = random.randint(7,10)
    n2 = random.randint(10,15)
    pid = str(random.randint(10**(n1-1),10**(n2-1)))
    project_dict = {username:{"projects":{pid:{"project_name": file_name[:-4], "ordering":"","cards":{}}}}}
    project_dict_cards = project_dict[username]['projects'][pid]['cards']
   
    for i in d:
        
        id =  str(int(datetime.now().timestamp()) + random.randint(10**(n1-1),10**(n2-1)))
        i['id']=id
        project_dict_cards[id] = i

    print(d)
    fpath = f'users/{username}_projects.json'
    if os.path.isfile(fpath):
        with open(file_path) as json_file:
            dictionary = json.load(json_file)
        dictionary[username]['projects'][pid] = project_dict[username]['projects'][pid]
        write_to_json(dictionary,file_path)
        return True
    else:
        write_to_json(project_dict,file_path)
        return True



def write_user_to_json(username,d,file_path):
    dictionary = {username:d}
    # Serializing json 
    json_object = json.dumps(dictionary, indent = 4)
    
    # Writing to sample.json
    with open(file_path, "w") as outfile:
        print('Writing to file',file_path)
        outfile.write(json_object)
    return True

def write_to_json(dictionary,file_path):
    # Serializing json 
    json_object = json.dumps(dictionary, indent = 4)
    
    # Writing to sample.json
    with open(file_path, "w") as outfile:
        print('Writing to file',file_path)
        outfile.write(json_object)
    return True

# def append_to_txt(line,file_path="users/all_users.txt"):
#     with open(file_path, "a") as myfile:
#         myfile.write(line+'\n')




def save_project_to_json(dictionary,username,project_id):
    try:
        file_path = f'users/{username}_projects.json'
        projects_dict = copy.deepcopy(dictionary)
        # print('Original dict: ',projects_dict)
        for project_id in dictionary[username]['projects']:
            cards = dictionary[username]['projects'][project_id]['cards']
            for card in cards:
                projects_dict[username]['projects'][project_id]['cards'][card] = dictionary[username]['projects'][project_id]['cards'][card].__dict__

        # print('Save dict: ',projects_dict)
        write_to_json(projects_dict,file_path)
        return True
    except Exception as e:
        print(e)
        return False

def read_response_json(file_path,username):
    with open(file_path) as json_file:
        dictionary = json.load(json_file)
    return dictionary

def read_json(file_path,username):
    with open(file_path) as json_file:
        dictionary = json.load(json_file)
        projects_dict = copy.deepcopy(dictionary)
    print(projects_dict)
    for project_id in dictionary[username]['projects']:
        cards = dictionary[username]['projects'][project_id]['cards']
        for card in cards:
            card_details = dictionary[username]['projects'][project_id]['cards'][card]

            c = FormCard(card_details['id'],card_details['answer_type'])
            c.set_values(card_details['question'],card_details['options'],card_details['answers'],card_details['score'],card_details['required'])

            projects_dict[username]['projects'][project_id]['cards'][card] = c
    print("File Data",projects_dict)
    return projects_dict


class User:
    def __init__(self,username,email,password,setupComplete):
        self.username = username 
        self.email = email 
        self.password = password
        self.setupComplete = setupComplete
        self.file_path ="users/"+username + '.json'
        self.dictionary ={
            "email" :email,
            "password" : password,
            "setupComplete" : self.setupComplete
           
        }
        write_user_to_json(username,self.dictionary,self.file_path)
        # line = f'{username} {email} {password}'
        # append_to_txt(line)

    def __repr__(self):
        return self.email

    def get(self,id):

        return self.email , self.password

    def setup_complete(self,setupComplete,name,usingFor,industry,org,role,activity,howFound):
        self.setupComplete = setupComplete
        self.name = name
        self.usingFor = usingFor
        self.industry = industry
        self.org = org
        self.role = role
        self.activity = activity
        self.howFound = howFound

        self.dictionary['setupComplete'] = setupComplete
        self.dictionary["name"] = name
        self.dictionary["usingFor"] = usingFor
        self.dictionary["industry"] = industry
        self.dictionary["org"] = org
        self.dictionary["role"] = role
        self.dictionary["activity"] = activity
        self.dictionary["howFound"] = howFound

        write_user_to_json(self.username,self.dictionary,self.file_path)

class FormCard:
    def __init__(self,id,answer_type):
        self.id =id
        self.question =None
        self.options = []
        self.answers = None 
        self.answer_type = answer_type
        self.score = None
        self.required = True
        

    def set_values(self,question,options,answers,score,required):
        self.question =question
        self.options = options
        self.answers = answers 
        self.score = score
        self.required = required
      
    
    