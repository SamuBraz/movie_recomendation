from ...extensions import db


class User(db.Model):
    __tablename__ = 'User'

    userId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)



    def __repr__(self):
        return "<USER self.name self.email>"
    

    def get_id(self):
        return self.userId