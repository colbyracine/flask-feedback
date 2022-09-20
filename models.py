from types import ClassMethodDescriptorType
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database"""
    
    db.app = app
    db.init_app(app)
    
class User(db.Model):
    
    #create table name as 'users'
    
    __tablename__= 'users'
    
    #create columns for db
    
    username = db.Column(db.String(20), unique=True, primary_key=True )
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    
    children = relationship("Feedback", cascade="all,delete", backref="users")
    
    
    #classmethod to register new user and hash password*********
    
    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """register user w/hashed password & return user"""
    
        hashed = bcrypt.generate_password_hash(pwd)
        # turn instance of user w/username and hashed pwd
        hashed_utf8 = hashed.decode("utf8")
        
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate user exists & pwd correct
        
        Retrun user if valid: else return False"""
        
        u = User.query.filter_by(username=username).first()
        
        if u and bcrypt.check_password_hash(u.password, pwd):
            
            return u
        else:
            return False
        
class Feedback(db.Model):
    
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(30), db.ForeignKey('users.username'))
    
    user = db.relationship('User', backref="feedback")


        
        