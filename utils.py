from functools import wraps
from flask import g, request, redirect, url_for
from models import *
import pandas as pd
import random
from datetime import datetime
import numpy as np
import os

form_start_indicator = "Start"
form_end_indicator = "Default End"

# root_path = '/home/shilpa/mysite/users/'
root_path = 'users/'

def excel_to_json(username, file_name):
    file_path = root_path + file_name
    df = pd.read_csv(file_path)
    print(df.shape)
    # print(df)
    df.columns= df.columns.str.strip().str.lower()	

    cols = ['project_name','total_time(project)','question', 'options', 'answer_type', 'answers', 'score', 'required']
    for i in cols:
        if i not in df.columns:
            return False
    project_name = df['project_name'].iloc[0]
    if project_name!=project_name:
        project_name = file_name[:-4]
    
    project_time = df['total_time(project)'].iloc[0]

    if project_time!=project_time:
        project_time = 0
    else:
        if project_time < 0:
            project_time = 0
        elif project_time > 180:
            project_time = 180

    df = df[['question', 'options', 'answer_type', 'answers', 'score', 'required']]
    # if anser_type contians return failed

    if df['answer_type'].isnull().values.any():
        return False

    df['question'] = df['question'].fillna("")

    df['options'] = df['options'].str.replace('[','',1)
    df['options'] = df['options'].str.replace(']','',1)
    df['options'] = df['options'].str.split(',')
    df['options'] = df['options'].replace('[]',np.nan)
    isna = df['options'].isna()
    df.loc[isna, 'options'] = pd.Series([[""]] * isna.sum()).values


    # validate if options match the answer type. Also check length of options shouldn't be greater than a threshold

    # fill required with True
    df['required'] = df['required'].fillna(True)

    # check if there are any other values other name True , False

    df =df.replace({np.nan: None})

    d = df.to_dict('records')
    n1 = random.randint(7,10)
    n2 = random.randint(10,15)
    pid = str(random.randint(10**(n1-1),10**(n2-1)))
    project_dict = {username:{"projects":{pid:{"project_name":project_name ,"total_time":project_time, "ordering":{},"cards":{}}}}}
    project_dict_cards = project_dict[username]['projects'][pid]['cards']

    for i in d:

        id =  str(int(datetime.now().timestamp()) + random.randint(10**(n1-1),10**(n2-1)))
        i['id']=id
        project_dict_cards[id] = i


    project_dict = default_ordering_multi_card(username,pid,project_dict)
    # print('ordered----------------',project_dict)
    fpath = f'{root_path}{username}_projects.json'
    if os.path.isfile(fpath):
        with open(fpath) as json_file:
            dictionary = json.load(json_file)
        dictionary[username]['projects'][pid] = project_dict[username]['projects'][pid]
        write_to_json(dictionary,fpath)
        # os.remove(file_path)
        return True
    else:
        write_to_json(project_dict,fpath)
        # os.remove(file_path)
        return True



def default_ordering_multi_card(username,project_id,projects_info):

    cards = [form_start_indicator]
    cards.extend(projects_info[username]['projects'][project_id]['cards'].keys())
    cards.append(form_end_indicator)
    for i in range(len(cards)-1):
        projects_info[username]['projects'][project_id]['ordering'][cards[i]] = cards[i+1]
    return projects_info

def default_ordering(username,project_id,projects_info):

    project_cards = tuple(projects_info[username]['projects'][project_id]['cards'].keys())
    ordering = projects_info[username]['projects'][project_id]['ordering']

    if len(ordering)<=0 and len(project_cards)==1:
        ordering[form_start_indicator] = project_cards[0]
        ordering[project_cards[0]] = form_end_indicator

    if len(ordering)<=0 and len(project_cards)>1:
        projects_info = default_ordering_multi_card(username,project_id,projects_info)

    if len(ordering)>0 and len(project_cards) > len(ordering)-1 and len(set(project_cards) - ( set(ordering.keys()) - set((form_start_indicator)) ) )==1:
        new_card = tuple(set(project_cards) - set(ordering.keys()))
        end_key = tuple(ordering.keys())[tuple(ordering.values()).index(form_end_indicator)]

        ordering[end_key] =  new_card[0]
        ordering[new_card[0]] = form_end_indicator

    print("default ordering complete")
    # print('ordering',projects_info[username]['projects'][project_id]['ordering'])
    return projects_info




def check_loop_logic(ordering):
    # check if loop exists
    loop_list = []
    loop_exists = False
    print('in check loop')
    next = ordering['Start']
    loop_list.append(next)

    while loop_exists == False:
        print(loop_list)
        next = ordering[next]
        if next in loop_list:
            loop_exists = True
            break
        if next == 'Default End':
            break
        loop_list.append(next)
    return loop_exists


def save_project(projects_info,username,project_id):
    res = save_project_to_json(projects_info,username,project_id)
    if res ==False:
        return '4'
    else:
        return '3'


# details -  https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         print('in decorator')
#         if active_username is None:
#             print('no user')
#             return redirect(url_for('login', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function