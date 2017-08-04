import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config.from_object(os.getenv('APP_SETTINGS'))
api = Api(app, prefix='/api/V1')
db = SQLAlchemy(app)
db.create_all()

db_engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))
session = sessionmaker(bind=db_engine)()
SECRET_KEY = app.config.get('SECRET_KEY')

from app.controller.endpoints import api_endpoints
api_endpoints(api)
