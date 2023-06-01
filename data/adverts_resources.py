import re
from datetime import datetime

from flask import jsonify
from flask_restful import Resource, abort

from . import db_session
from .adverts import Advert
from .reqparse_adverts import parser


def abort_if_advert_not_found(advert_id):
    session = db_session.create_session()
    adverts = session.get(Advert, advert_id)
    if not adverts:
        abort(404, message=f"Advert {advert_id} not found")


class AdvertsResource(Resource):
    def get(self, advert_id):
        abort_if_advert_not_found(advert_id)
        session = db_session.create_session()
        adverts = session.get(Advert, advert_id)
        return jsonify({'advert': adverts.to_dict(only=('name', 'id_person', 'description', 'price', 'data',
                                                        'id_files'))})

    def delete(self, advert_id):
        abort_if_advert_not_found(advert_id)
        session = db_session.create_session()
        advert = session.get(Advert, advert_id)
        session.delete(advert)
        session.commit()
        return jsonify({'success': 'OK'})


class AdvertsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        adverts = session.query(Advert).all()
        return jsonify({'adverts': [item.to_dict(only=('name', 'id_person', 'description', 'price', 'data',
                                                       'id_files')) for item in adverts]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        advert = Advert(
            name=args['name'],
            id_person=args['id_person'],
            description=args['description'],
            price=args['price'],
            data=datetime.strptime(args['data'], '%Y-%m-%d %H:%M:%S.%f'),
            for_search=re.sub(r'\W', '', (args['name'] + args['description'])).lower())
        session.add(advert)
        session.commit()
        return jsonify({'success': 'OK'})
