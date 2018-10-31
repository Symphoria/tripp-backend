from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_cors import CORS
from flask_basicauth import BasicAuth
from flask_admin.contrib import sqla
from werkzeug.exceptions import HTTPException


app = Flask(__name__)
app.config.from_object('config')

CORS(app)
db = SQLAlchemy(app)
basic_auth = BasicAuth(app)
admin = Admin(app, template_mode='bootstrap3')

from models import *
from views import *

db.create_all()


class AuthException(HTTPException):
    def __init__(self, message):
        super(AuthException, self).__init__(message, Response(
            "You could not be authenticated. Please refresh the page.", 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ))


class ModelView(sqla.ModelView):
    def is_accessible(self):
        if not basic_auth.authenticate():
            raise AuthException('Not authenticated.')
        else:
            return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(basic_auth.challenge())


admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(Reservation, db.session))
