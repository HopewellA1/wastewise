from main import db
from datetime import date
from flask_login import UserMixin



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100),unique=True, nullable=False)
    password = db.Column(db.String(200))
    is_superuser = db.Column(db.Boolean, default=False)
    is_staff = db.Column(db.Boolean, default=False)
    date_joined = db.Column(db.Date, default=date.today())
    
    def __init__(self, fname, lname, email,password,is_superuser = False, is_staff = False, is_active = False, ):
        self.first_name = fname
        self.last_name = lname
        self.email = email
        self.password = password
        #self.is_active = is_active
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        
    def __repr__(self):
        return f"<User {self.email} >"
        
        