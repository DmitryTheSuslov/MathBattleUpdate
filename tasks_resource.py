import parser
from flask_restful import reqparse, abort, Api, Resource

from flask import Flask, Blueprint, jsonify, request
from data import db_session
from data.__all_models import *


parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('content', required=True)
parser.add_argument('answer', required=True)
parser.add_argument('points', required=True, type=int)
parser.add_argument('user_login', required=True)


def abort_if_task_not_found(task_id):
    """Обработка ситуации, при которой в запросе указывается не существующий элемент"""
    session = db_session.create_session()
    task = session.query(Task).filter(Task.id == task_id).first()
    if not task:
        abort(404, message=f"Task {task_id} not found")


class TaskResource(Resource):
    def get(self, task_id):
        """Функция, обрабатывающая get запрос и возвращающая один объект"""
        session = db_session.create_session()
        if int(task_id):
            abort_if_task_not_found(task_id)
            tasks = session.query(Task).filter(Task.id == task_id).first()
            return jsonify({'name': tasks.name, 'content': tasks.content, 'answer': tasks.answer,
                            'points': tasks.points, 'user_login': tasks.user_login, 'id': tasks.id})
        else:
            count = list(reversed(session.query(Task).order_by(Task.id).all()))[0].id
            return jsonify({'count': count})

    def put(self, task_id):
        """Функция, обрабатывающая put запрос и изменяющая один объект"""
        session = db_session.create_session()
        task = session.query(Task).filter(Task.id == task_id).first()
        task.reports += 1
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})

    def delete(self, task_id):
        """Функция, обрабатывающая delete запрос и удаляющая один объект"""
        session = db_session.create_session()
        task = session.query(Task).filter(Task.id == task_id).first()
        session.delete(task)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class TaskListResource(Resource):
    """Функция, обрабатывающая get запрос и возвращающая список объектов"""
    def get(self, user_login):
        session = db_session.create_session()
        if user_login != "'":
            tasks = session.query(Task).filter(Task.user_login == user_login).all()
        else:
            tasks = reversed(session.query(Task).order_by(Task.reports).all())
        return jsonify({'tasks': [{'name': task.name, 'content': task.content, 'answer': task.answer,
                                  'points': task.points, 'user_login': task.user_login, 'id': task.id,
                                   'reports': task.reports} for task in tasks]})

    def post(self, user_login):
        """Функция, обрабатывающая post запрос и добавляющая один объект"""
        print(1)
        args = parser.parse_args()
        session = db_session.create_session()
        task = Task(
            name=args['name'],
            content=args['content'],
            answer=args['answer'],
            points=args['points'],
            user_login=args['user_login']
        )
        session.add(task)
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, user_login):
        """Функция, обрабатывающая delete запрос и удаляющая список объектов"""
        session = db_session.create_session()
        tasks = session.query(Task).filter(Task.user_login == user_login).all()
        for task in tasks:
            session.delete(task)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})