from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy import orm
import sqlalchemy


class Answer(SqlAlchemyBase, UserMixin):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True)
    user = orm.relation('User')
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tasks.id'), nullable=True)
    task = orm.relation('Task')
