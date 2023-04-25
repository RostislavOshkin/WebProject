from flask import jsonify
from flask_restful import Resource, abort
from werkzeug.security import generate_password_hash

from . import db_session
from .users import User
from .reqparse_user import parser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    users = session.get(User, user_id)
    if not users:
        abort(404, message=f"User {user_id} not found")


def set_password(password):
    return generate_password_hash(password)


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        users = session.get(User, user_id)
        return jsonify({'user': users.to_dict(only=('name', 'description', 'address',
                                                    'password'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(only=('name', 'description', 'address',
                                                     'password')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            description=args['description'],
            address=args['address'],
            password=set_password(args['password'])
        )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
