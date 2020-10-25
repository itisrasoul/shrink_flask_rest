#Import os to read configs in env files with
import os

#Create a class for config
class Config(object):
    FLASK_ENV = os.getenv('FLASK_ENV')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_BLACKLIST_ENABLED = os.getenv('JWT_BLACKLIST_ENABLED')
    REDIS_SERVER_URL = os.getenv('REDIS_SERVER_URL')