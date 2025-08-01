
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    UserId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False, unique=True)
    Email = db.Column(db.String(120), nullable=False, unique=True)
    Password = db.Column(db.String(200), nullable=False)
    DisplayName = db.Column(db.String(120))
    Image = db.Column(db.String(200))  # Store image filename or path
