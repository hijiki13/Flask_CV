from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Users(db.Model):
    __tablename__ = 'registeredUsers'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String)
    password = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    fathers_name = db.Column(db.String)
    birthdate = db.Column(db.String)
    LinkedIn = db.Column(db.String)
    tel = db.Column(db.String)
    education = db.Column(db.String)
    skills = db.Column(db.String)
    experience = db.Column(db.String)
    u_img = db.Column(db.String)
