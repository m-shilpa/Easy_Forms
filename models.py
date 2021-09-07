import json
import copy

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
        return False


def read_json(file_path,username):
    with open(file_path) as json_file:
        dictionary = json.load(json_file)
        projects_dict = copy.deepcopy(dictionary)

    for project_id in dictionary[username]['projects']:
        cards = dictionary[username]['projects'][project_id]['cards']
        for card in cards:
            card_details = dictionary[username]['projects'][project_id]['cards'][card]

            c = FormCard(card_details['id'],card_details['answer_type'])
            c.set_values(card_details['question'],card_details['options'],card_details['answers'],card_details['score'],card_details['position'])

            projects_dict[username]['projects'][project_id]['cards'][card] = c
    # print("File Data",projects_dict)
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
        write_to_json(self.dictionary,self.file_path)
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

        self.dictionary["name"] = name
        self.dictionary["usingFor"] = usingFor
        self.dictionary["industry"] = industry
        self.dictionary["org"] = org
        self.dictionary["role"] = role
        self.dictionary["activity"] = activity
        self.dictionary["howFound"] = howFound

        write_to_json(self.dictionary,self.file_path)

class FormCard:
    def __init__(self,id,answer_type):
        self.id =id
        self.question =None
        self.options = []
        self.answers = None 
        self.answer_type = answer_type
        self.score = None
        self.position = None

    def set_values(self,question,options,answers,score,position):
        self.question =question
        self.options = options
        self.answers = answers 
        self.score = score
        self.position = position
    
    