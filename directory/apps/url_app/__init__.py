#Import Libs
from flask import Blueprint

#Initialize url Blueprint
url = Blueprint('url', __name__, url_prefix='/url/')

from . import views

# 127.0.0.1:5000/url/shrink

# 127.0.0.1:5000/url/ (shrink) -> POST

# 127.0.0.1:5000/url/ (check) -> GET

# 127.0.0.1:5000/url/ (delete) -> DELETE