import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://new_username:new_password@localhost/quiz_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False