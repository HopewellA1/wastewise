from main import db
from datetime import date, datetime, timezone
#from .auth import User


class Participant(db.Model):
    
    Participant_Id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    PhoneNumber = db.Column(db.String(15),nullable=False )
    PhysicalAddress= db.Column(db.String(250), nullable=False)
    points = db.Column(db.Integer, default=int())
    total_points_accumulated = db.Column(db.Integer, default=int())
    created_at = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc))
    
    def __init__(self, user_id, PhoneNumber, PhysicalAddress):
        
        self.user_id = user_id
        self.PhoneNumber = PhoneNumber
        self.PhysicalAddress = PhysicalAddress
        
    def __repr__(self):
        return f'<Participant({self.Participant_Id}) >'
        
    
    
    
class Reward(db.Model):
    
    Reward_Id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attribute_name = db.Column(db.String(200))  
    points_required = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationships
    participant_rewards = db.relationship('ParticipantReward', backref='reward', lazy=True)
    
    def __repr__(self):
        return f'<Reward {self.attribute_name}>'

class Category(db.Model):
    Category_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #admin/superuser user
    Name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Active")
    created_at = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc))
    
    def __init__(self, user_id,Name ):
        
        self.user_id = user_id
        self.Name = Name
    
    def __repr__(self):
        return f'<Category: {self.Name}({self.Category_id})'
        
    
    


    
class Contribution(db.Model):
    
    Contribution_Id = db.Column(db.Integer, primary_key=True)
    Participant_Id = db.Column(db.Integer, db.ForeignKey('participant.Participant_Id'), nullable=False)
    Category_id = db.Column(
        db.Integer,
        db.ForeignKey('category.Category_id', name='fk_contribution_category'),
        nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Admin who reviews the contribution
    quantity = db.Column(db.Integer, default=int())
    points_awarded = db.Column(db.Integer, default=int())
    item_type = db.Column(db.String(60),nullable= True )
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Draft")
    
    def __init__(self,Participant_Id, user_id,Category_id, item_type, quantity, description, status = "Daft"):
        self.Participant_Id = Participant_Id
        self.Category_id = Category_id
        self.user_id = user_id
        self.item_type = item_type
        self.quantity = quantity
        self.description =description
        
    timestamp = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Contribution: {self.Contribution_Id}>'


class Product(db.Model):
    
    ProductId = db.Column(db.Integer, primary_key=True)
    Contribution_Id = db.Column(db.Integer, db.ForeignKey('contribution.Contribution_Id'), nullable=False)
    Product_Name = db.Column(db.String(200), nullable=False)
    Image = db.Column(db.String(500)) 
    decription = db.Column(db.String(5000), nullable=True)
    
    def __init__(self, contri_id, Product_Name,Image, decription):
        self.Contribution_Id = contri_id
        self.Product_Name = Product_Name
        self.Image = Image
        self.decription = decription
        
    
    def __repr__(self):
        return f'<Product {self.Product_Name}({self.ProductId})>'
    

class ParticipantReward(db.Model):
    
    ParticipantReward_ID = db.Column(db.Integer, primary_key=True)
    Reward_Id = db.Column(db.Integer, db.ForeignKey('reward.Reward_Id'), nullable=False)
    Participant_Id = db.Column(db.Integer, db.ForeignKey('participant.Participant_Id'), nullable=False)
    date_claimed = db.Column(db.DateTime, default=lambda:datetime.now(timezone.utc))
    points_used = db.Column(db.Integer)  
    balancePoints = db.Column(db.Integer)
    def __repr__(self):
        return f'<ParticipantReward {self.ParticipantReward_ID}>'
