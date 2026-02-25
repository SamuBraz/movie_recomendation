from ...extensions import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)



    def __repr__(self):
        return "<USER self.name self.email>"
    

    def get_id(self):
        return self.user_id