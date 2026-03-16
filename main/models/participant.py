from main import db
from datetime import date, datetime
#from .auth import User


class Participant(db.Model):
    
    ParticipantId = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    PhoneNumber = db.Column(db.String(15),nullable=False )
    PhysicalAddress= db.Column(db.String(250), nullable=False)
    points = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    
    
class Reward(db.Model):
    
    Reward_Id = db.Column(db.Integer, primary_key=True)
    Admin_Id = db.Column(db.Integer, db.ForeignKey('admin.Admin_Id'), nullable=False)
    attribute_name = db.Column(db.String(200))  
    points_required = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationships
    participant_rewards = db.relationship('ParticipantReward', backref='reward', lazy=True)
    
    def __repr__(self):
        return f'<Reward {self.attribute_name}>'
    
    
class Contribution(db.Model):
    
    Contribution_Id = db.Column(db.Integer, primary_key=True)
    Participant_Id = db.Column(db.Integer, db.ForeignKey('participant.Participant_Id'), nullable=False)
    AdminId = db.Column(db.Integer, db.ForeignKey('admin.Admin_Id'), nullable=True)  # Admin who reviews the contribution
    attribute_name = db.Column(db.String(200)) 
    points_awarded = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now().time())
    
    def __repr__(self):
        return f'<Contribution {self.Contribution_Id}>'


class Product(db.Model):
    
    ProductId = db.Column(db.Integer, primary_key=True)
    Contribution_Id = db.Column(db.Integer, db.ForeignKey('contribution.Contribution_Id'), nullable=False)
    Product_Name = db.Column(db.String(200), nullable=False)
    Image = db.Column(db.String(500)) 
    
    def __repr__(self):
        return f'<Product {self.Product_Name}>'
    

class ParticipantReward(db.Model):
    
    ParticipantReward_ID = db.Column(db.Integer, primary_key=True)
    Reward_Id = db.Column(db.Integer, db.ForeignKey('reward.Reward_Id'), nullable=False)
    Participant_Id = db.Column(db.Integer, db.ForeignKey('participant.ParticipantId'), nullable=False)
    date_claimed = db.Column(db.DateTime, default=datetime.now().time())
    points_used = db.Column(db.Integer)  
    balancePoints = db.Column(db.Integer)
    def __repr__(self):
        return f'<ParticipantReward {self.ParticipantReward_ID}>'
