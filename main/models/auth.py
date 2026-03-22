from main import db
from datetime import date, datetime, timezone
from flask_login import UserMixin



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100),unique=True, nullable=False)
    password = db.Column(db.String(200))
    is_superuser = db.Column(db.Boolean, default=False)
    is_staff = db.Column(db.Boolean, default=False)
    is_terms_accepted = db.Column(db.Boolean, default=False)
    is_account_active = db.Column(db.Boolean, default=False)
   # is_active = db.Column(db.Boolean, default=True)
    date_joined = db.Column(db.Date, default=lambda:datetime.now(timezone.utc))
    
    def __init__(self, fname, lname, email,password,is_superuser = False, is_staff = False,is_terms_accepted= False, is_account_active= is_account_active ):
        self.first_name = fname
        self.last_name = lname
        self.email = email
        self.password = password
        self.is_terms_accepted = is_terms_accepted
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.is_account_active = is_account_active
        
    def is_active(self):
        return self.active
        
    def __repr__(self):
        return f"<User {self.email} >"
        
        
        
class OTP(db.Model):
    
    otp_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    status=db.Column(db.String(30), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc))
    
    def __init__(self, userId, code, status):
        
        self.user_id = userId
        self.code = code
        self.status = status
        
    def __repr__(self):
        return f"<OTP {self.code}"
        
    
 #check expiry:   
# from datetime import datetime, timezone, timedelta

# if datetime.now(timezone.utc) > otp.created_at + timedelta(minutes=5):
#     print("OTP expired")