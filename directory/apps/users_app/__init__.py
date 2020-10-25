#Import Libs
from flask import Blueprint

#Define a new blueprint for users mod
users = Blueprint('users', __name__, url_prefix='/users/')

#Import/Register Views for users blueprint
from . import views