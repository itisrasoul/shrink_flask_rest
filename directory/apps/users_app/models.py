#Import Libs
from sqlalchemy import Column, String, Integer
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
from directory.apps import db

#Create table in database / Create a db model
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), unique=False, nullable=False)

    #Create a function to validate and create password hash
    @validates('password')
    def generate_password(self, key, value):
        if value is None:
            raise ValueError('Password can\'nt be null.')
        #Check the password length
        if len(value) < 8:
            raise ValueError('Password Must be at least 8 characters.')
        #Generate password hash
        return generate_password_hash(value)

    #Create a function to validate username
    @validates('username')
    def validate_username(self, key, value: str):
        if value is None:
            raise ValueError('Username can\'t be null.')
        #Check if the username is an identifier
        if not value.isidentifier():
            raise ValueError('Invalid username.')
        return value

    #Create a function to check the password hash
    def check_password(pass_hash, password):
        return check_password_hash(pass_hash, password)