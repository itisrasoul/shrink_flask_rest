#Import Libs
from sqlalchemy import Column, Integer, String
from directory.apps import db

#Create a database model for storing urls
class URL(db.Model):
    __tablename__ = 'url'
    id = Column(Integer(), primary_key = True, unique = True, nullable = False)
    original_url = Column(String(512), unique = False, nullable = False)
    short_url = Column(String(128), unique = True, nullable = False)
    username = Column(String(32), unique = False, nullable = False)