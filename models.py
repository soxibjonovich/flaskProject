from enum import Enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class TaskType(Enum):
    GroupToGroupDate = "group2group"
    ChannelDate = "channel"
    PrivateChat = "private"
    PrivateChatForce = "private_force"


class Status(Enum):
    Active = "active"
    Inactive = "inactive"


class OrderType(Enum):
    GroupToGroup = "group2group"
    Channel = "channel"


class HashStatus(Enum):
    live = "tirik"
    died = "o'lik"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    twofacode = db.Column(db.String(256))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(generate_password_hash(self.password), password)


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_type = db.Column(db.Enum(TaskType), nullable=False)
    hash = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hash_added_date = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    link = db.Column(db.String, nullable=False)
    task_author = db.Column(db.String, nullable=False)

    def get_tasks_for_user_id(self, user_id: int):
        return self.query.filter_by(user_id=user_id).all()


class Hashes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    work_status = db.Column(db.Enum(Status), nullable=False)
    hash_status = db.Column(db.Enum(HashStatus), nullable=False)
    hash_added_date = db.Column(db.DateTime, default=datetime.utcnow)
    phone_number = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    telegram_id = db.Column(db.String, unique=True, nullable=False)
    clone_device_name = db.Column(db.String, nullable=False)

    def get_tasks_for_user_id(self, user_id: int):
        return self.query.filter_by(user_id=user_id).all()

    @staticmethod
    def check_phone_number(phone_number: str):
        return Hashes.query.filter_by(phone_number=phone_number).first() is not None


class TaskHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_type = db.Column(db.Enum(TaskType), nullable=False)
    task_added_date = db.Column(db.DateTime, nullable=False)
    task_expire_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    hash_count = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    link = db.Column(db.String, nullable=False)
    task_author = db.Column(db.String, nullable=False)

    def get_tasks_from_user_id(user_id: int):
        return TaskHistory.query.filter_by(user_id=user_id).all()


class InProgressHashes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hash = db.Column(db.String, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hash_status = db.Column(db.Enum(HashStatus), nullable=False)
    hash_added_date = db.Column(db.DateTime, default=datetime.utcnow)
    phone_number = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    telegram_id = db.Column(db.String, unique=True, nullable=False)
    clone_device_name = db.Column(db.String, nullable=False)

    def get_tasks_for_user_id(self, user_id: int):
        return self.query.filter_by(user_id=user_id).all()

    @staticmethod
    def check_phone_number(phone_number: str):
        return Hashes.query.filter_by(phone_number=phone_number).first() is not None
