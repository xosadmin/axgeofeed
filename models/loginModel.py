from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, role):
        self.id = id
        self.role = role

    def get_ID(self):
        return self.id

    def get_role(self):
        return self.role