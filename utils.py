from functools import wraps
from flask import g, request, redirect, url_for
from models import *

form_start_indicator = "Start"
form_end_indicator = "Default End"

def default_ordering_multi_card(username,project_id,projects_info):

    cards = [form_start_indicator]
    cards.extend(projects_info[username]['projects'][project_id]['cards'].keys())
    cards.append(form_end_indicator)
    for i in range(len(cards)-1):
        projects_info[username]['projects'][project_id]['ordering'][cards[i]] = cards[i+1]

def default_ordering(username,project_id,projects_info):

    project_cards = tuple(projects_info[username]['projects'][project_id]['cards'].keys())
    ordering = projects_info[username]['projects'][project_id]['ordering']
   
    if len(ordering)<=0 and len(project_cards)==1:
        ordering[form_start_indicator] = project_cards[0]
        ordering[project_cards[0]] = form_end_indicator
    
    if len(ordering)<=0 and len(project_cards)>1:
        default_ordering_multi_card(username,project_id,projects_info)

    if len(ordering)>0 and len(project_cards) > len(ordering)-1 and len(set(project_cards) - ( set(ordering.keys()) - set((form_start_indicator)) ) )==1:
        new_card = tuple(set(project_cards) - set(ordering.keys()))
        end_key = tuple(ordering.keys())[tuple(ordering.values()).index(form_end_indicator)]
      
        ordering[end_key] =  new_card[0]
        ordering[new_card[0]] = form_end_indicator
    
    print("default ordering complete")
    print('ordering',projects_info[username]['projects'][project_id]['ordering'])




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