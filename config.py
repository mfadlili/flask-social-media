import os

class Config(object):
    SECRET_KEY = 'mysecret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///myDB.db'
    SQLALCHEMY_TRACK_MODIFICATION = False