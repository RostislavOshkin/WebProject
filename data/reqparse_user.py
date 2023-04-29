from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('description', required=True)
parser.add_argument('address', required=True)
parser.add_argument('password', required=True)
parser.add_argument('communication', required=True)
