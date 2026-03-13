from main import db
from datetime import date
#from .auth import User


class Participant(db.Model):
    
    ParticipantId = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    PhoneNumber = db.Column(db.String(15),nullable=False )
    PhysicalAddress= db.Column(db.String(250), nullable=False)
    points = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    