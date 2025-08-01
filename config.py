import os

class Config:
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres:13Dhillon%40nz@localhost:5432/TeePal"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'users')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
