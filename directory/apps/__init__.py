#Import Libs
from flask import Flask, abort, redirect, url_for
from .config import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from urllib.parse import urlparse, urlunparse
from redis import Redis

#Initialize the flask app
app = Flask(__name__)

#Config the flask app
app.config.from_object(Config)
#Configure JWT_BLACKLIST_TOKEN_CHECKS seperately, because it does not recognize lists in .env file
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

#Initialize SQLALCHEMY ORM
db = SQLAlchemy(app)

#Initialize flask migrate
migrate = Migrate(app, db)

#Intialize JWTManager
jwt_manager = JWTManager(app)

#Initialize redis for blacklist tokens
token_container = Redis.from_url(app.config['REDIS_SERVER_URL'])

#Import URL database model
from .url_app.models import URL

#Register Blueprints
from .users_app import users
app.register_blueprint(users)

from .url_app import url
app.register_blueprint(url)

#set route for main index of app
@app.route('/<url>', methods=['GET'])
def index(url):
    #Search for original url in database
    database_url = URL.query.filter(URL.short_url.ilike(url_for('index', url=url, _external=True))).first()
    
    ## Add http to url if not exist, because flask redirect identifies URLs without http as in-app routes

    url_parts = list(urlparse(database_url.original_url))
    if url_parts[0] != 'http' or url_parts[0] != 'https':
        url_parts[0] = 'http'
        url_parts[1] = '://'
        url_converted = "".join(url_parts)
        print(url_converted)
    if not database_url:
        abort(404)

    #Redirect to original url
    return redirect(url_converted, 302)