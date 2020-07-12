from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import orm
import sqlalchemy


class ForumAnswer(SqlAlchemyBase, UserMixin):
    __tablename__ = 'forum_answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    datetime = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=datetime.strftime(datetime.now(),
                                                                                             '%d.%m.%y %H:%M'))
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True)
    user = orm.relation('User')
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('forum_tasks.id'), nullable=True)
    task = orm.relation('ForumTask')
