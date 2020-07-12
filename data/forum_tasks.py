from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import orm
import sqlalchemy


class ForumTask(SqlAlchemyBase, UserMixin):
    __tablename__ = 'forum_tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    str_id = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=str(id).ljust(4, '0'))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    short_description = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=content)
    views = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=1)
    answers = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    datetime = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=datetime.strftime(datetime.now(),
                                                                                             '%d.%m.%y %H:%M'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=True)
    user = orm.relation('User')
