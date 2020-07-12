import parser

from flask_restful import reqparse, abort, Api, Resource

from flask import Flask, Blueprint, jsonify, request
from data import db_session
from data.__all_models import *


parser = reqparse.RequestParser()
parser.add_argument('nickname', required=True)
parser.add_argument('status', required=True)
parser.add_argument('login', required=True)
parser.add_argument('hashed_password', required=True)
parser.add_argument('birthday', required=True)


def abort_if_user_not_found(user_login):
    """Обработка ситуации, при которой в запросе указывается не существующий элемент"""
    session = db_session.create_session()
    user = session.query(User).filter(User.login == user_login).first()
    if not user:
        abort(404, message=f"User {user_login} not found")


class UserResource(Resource):
    """Функция, обрабатывающая put запрос и изменяющая один объект"""
    def put(self, user_login):
        reported = request.form['reported']
        decided = request.form['decided']
        points = int(request.form['points'])
        session = db_session.create_session()
        user = session.query(User).filter(User.login == user_login).first()
        if int(decided):
            print(decided)
            user.decided_tasks += '%' + decided
        if int(reported):
            user.reports += '%' + reported
            print(reported)
        user.points += points
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    def delete(self, user_login):
        """Функция, обрабатывающая delete запрос и удаляющая один объект"""
        session = db_session.create_session()
        user = session.query(User).filter(User.login == user_login).first()
        session.delete(user)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    def get(self, user_login):
        """Функция, обрабатывающая get запрос и возвращающая один объект"""
        abort_if_user_not_found(user_login)
        session = db_session.create_session()
        user = session.query(User).filter(User.login == user_login).first()
        return jsonify({'nickname': user.nickname, 'status': user.status, 'login': user.login,
                        'hashed_password': user.hashed_password, 'birthday': user.birthday,
                        'decided_tasks': user.decided_tasks, 'reports': user.reports, 'points': user.points, 'user_id': user.id})


class UserListResource(Resource):
    def post(self):
        """Функция, обрабатывающая post запрос и добавляющая один объект"""
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            nickname=args['nickname'],
            login=args['login'],
            hashed_password=args['hashed_password'],
            birthday=args['birthday']
        )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
