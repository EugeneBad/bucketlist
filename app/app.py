import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask


app = Flask(__name__)

app.config.from_object(os.getenv('APP_SETTINGS'))

db = SQLAlchemy(app)
