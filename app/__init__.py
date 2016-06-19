from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('app.config')
db = SQLAlchemy(app)

from app import views, models
