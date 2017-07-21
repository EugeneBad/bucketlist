import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.getenv('APP_SETTINGS'))

api = Api(app)
db = SQLAlchemy(app)
db.create_all()

from app.api.endpoints import api_endpoints
api_endpoints(api)
