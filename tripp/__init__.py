from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object('config')

CORS(app)
db = SQLAlchemy(app)
admin = Admin(app, template_mode='bootstrap3')

from models import *
from views import *

db.create_all()

admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(Reservation, db.session))
