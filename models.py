class User:
    def __init__(self,id,email,password):
        self.id = id 
        self.email = email 
        self.password = password

    def __repr__(self):
        return self.email

    def get(self):
        return self.email , self.password