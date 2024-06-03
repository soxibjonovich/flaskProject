from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        print(self.password)
        return check_password_hash(generate_password_hash(self.password), password)


# def get_hashes(id: int):
#     return  UserHash.query.filter_by(added_userid=id).all()


# class UserHash(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     hash = db.Column(db.String(700), nullable=False)
#     added_userid = db.Column(db.Integer, nullable=False)
