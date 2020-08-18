from flask import Flask, render_template, url_for
import tasks_resource, users_resource
from flask_restful import Api
import os
from data import db_session

db_session.global_init('db/DataBase.sqlite')
app = Flask(__name__)


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    from api import *

    session = db_session.create_session()
    api.add_resource(users_resource.UserResource, '/api/users/<user_login>')
    api.add_resource(users_resource.UserListResource, '/api/user/')
    api.add_resource(tasks_resource.TaskResource, '/api/task/<task_id>')
    api.add_resource(tasks_resource.TaskListResource, '/api/tasks/<user_login>')
    main()
