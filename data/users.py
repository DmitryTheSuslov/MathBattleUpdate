import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='Новичок')
    points = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    # avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='/default_avatar.png')
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    decided_tasks = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='%0')
    birthday = sqlalchemy.Column(sqlalchemy.String, default='01.01.2000')
    reports = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='%0')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)