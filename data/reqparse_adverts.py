from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('id_person', required=True)
parser.add_argument('description', required=True)
parser.add_argument('price', required=True)
parser.add_argument('data', required=True)
parser.add_argument('id_files', required=True)
