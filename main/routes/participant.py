import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from main.models.participant import Contribution, Participant,Category, Product
from main.models.auth import User
from main import db, allowed_file, UPLOAD_FOLDER


    
    
participant = Blueprint("/participant", __name__, url_prefix="/participant")
#127.0.0.1:5000/participant/new
@participant.route('/new/<int:user_id>',methods=['POST', 'GET'])
@login_required
def new_participant(user_id):
    
    user = User.query.filter_by(id = user_id).first()
    if request.method == 'GET':
        
        return render_template('participant/new_participant.html', user= user)
    elif request.method == 'POST':
        
        participant = Participant(
            user_id=user_id,
            PhoneNumber= request.form.get("PhoneNumber"),
            PhysicalAddress = request.form.get("PhysicalAddress")
        )
        
        db.session.add(participant)
        db.session.commit()
        flash("Participant profile created successfully, welcome!", "success")
        return redirect(url_for('default.home'))
        
        # redirect to dash 
    
    
    pass





def update_participant(participant_id):
    participant = Participant.query.filter_by(Participant=participant_id).first()

    if not participant:
        flash("Participant not found", "danger")
        return redirect(url_for('default.home'))

    if request.method == 'GET':
        return render_template('participant/update_participant.html', participant=participant)

    elif request.method == 'POST':
        participant.PhoneNumber = request.form.get("PhoneNumber")
        participant.PhysicalAddress = request.form.get("PhysicalAddress")

        db.session.commit()
        flash("Participant updated successfully!", "success")
        return redirect(url_for('default.home'))

@participant.route('/contribution/<int:participant_id>', methods=['GET', 'POST'])
@login_required
    
def add_contribution(participant_id):
    participant_obj= Participant.query.filter_by(id=participant_id).first()

    if not participant_obj:
        flash("Participant not found", "danger")
        return redirect(url_for('default.home'))

    if request.method == 'GET':
        return render_template(
            'participant/add_contribution.html',
            participant=participant_obj
        )

    elif request.method == 'POST':
        amount = request.form.get("amount")

       

        try:
            amount = float(amount)
        except ValueError:
            flash("Invalid amount", "danger")
            return redirect(request.url)

        contribution = Contribution(
            participant_id=participant_obj.id,
            amount=amount
        )

        db.session.add(contribution)
        db.session.commit()

        flash("Contribution added successfully!", "success")
        return redirect(url_for('default.home'))


@participant.route('/update/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_participant(participant_id):
    participant = Participant.query.filter_by(Participant=participant_id).first()

    if not participant:
        flash("Participant not found", "danger")
        return redirect(url_for('default.home'))

    if request.method == 'GET':
        return render_template('participant/update_participant.html', participant=participant)

    elif request.method == 'POST':
        participant.PhoneNumber = request.form.get("PhoneNumber")
        participant.PhysicalAddress = request.form.get("PhysicalAddress")

        db.session.commit()
        flash("Participant updated successfully!", "success")
        return redirect(url_for('default.home'))

@participant.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template("participant/dashboard.html",
        user=get_user(current_user.id),
        leaderboard=get_leaderboard()[:3],
        challenges=[
            {"title": "Plastic Challenge", "progress": 70},
            {"title": "Weekly Goal",        "progress": 50},
        ],
        history=[
            {"type": "Bottles", "date": "Yesterday", "points": 50},
            {"type": "Paper",   "date": "3 days ago", "points": 30},
        ],
        referral={"link": "http://eco.com/ref/mbali", "count": 5, "points": 250},
        rewards=[{"name": "Gift Card", "description": "R50 voucher"}],
        resources=[{"title": "Eco Tips", "url": "http://eco.com/tips"}],
        updates=["New Recycling Initiative Launched!", "Tips for Reducing Waste at Home"],
    )



def get_user(user_id):
    user = User.query.get(user_id)
    participant = Participant.query.filter_by(user_id=user_id).first()
    return {"name": user.first_name, "points": participant.points, "rank": getRenk(user_id)}


def get_leaderboard():
    
    leaderboard = []
    
    participants = Participant.query.order_by(Participant.points.desc()).all()
    for participant in participants:
        
        user = User.query.get(participant.user_id)
        leaderboard.append(
            {"username": user.first_name,  "points": participant.points, "user_id": user.id}
        )
        
    
    return leaderboard


def getRenk(user_id):
    leaderboard = get_leaderboard()
    index = next((i for i, item in enumerate(leaderboard) if item["user_id"] == user_id), None)
    return index +1

# ── Leaderboard ───────────────────────────────────────────────────────────────

@participant.route('/leaderboard')
def leaderboard():
    user = get_user(current_user.id)
    return render_template("participant/leaderboard.html",
        leaderboard=get_leaderboard(),
        user_rank=user["rank"],
        user_points=user["points"],
    )

# ── Challenges ────────────────────────────────────────────────────────────────

@participant.route('/challenges')
def challenges():
    return render_template("participant/challenges.html",
        active_challenges=[
            {"title": "Plastic-Free Week",   "description": "Recycle 10 plastic items this week.",
             "progress": 70, "points": 100, "due": "Sunday"},
            {"title": "Weekly Goal",          "description": "Log at least 5 recycling entries.",
             "progress": 50, "points": 50,  "due": "Sunday"},
            {"title": "Glass Collector",      "description": "Recycle 5 glass bottles this month.",
             "progress": 20, "points": 75,  "due": "Month end"},
        ],
        completed_challenges=[
            {"title": "First Recycle",  "points": 25},
            {"title": "Paper Champion", "points": 60},
        ],
    )

# ── History ───────────────────────────────────────────────────────────────────

@participant.route('/history/<int:user_id>')
def history(user_id):
    
    user = User.query.get(user_id)
    participant = Participant.query.filter_by(user_id=user.id).first()
    contributions = Contribution.query.filter_by(Participant_Id=participant.Participant_Id)
    history = []
    categories = Category.query.all()
    for contri in contributions:
        history.append(
            {"status":contri.status,"type": contri.item_type, "quantity": contri.quantity,  "date": contri.timestamp, "points": contri.points_awarded,  "contri":contri}
        )
    return render_template("participant/history.html",history=history, categories = categories )


@participant.route('/detailed_recycle/<int:contri_id>', methods=['POST', 'GET'])
@login_required
def detailed_recycle(contri_id):
    
    contribution = Contribution.query.get(contri_id)
    participant= Participant.query.get(contribution.Participant_Id)
    Products = Product.query.filter_by(Contribution_Id=contribution.Contribution_Id)
    
    if request.method == 'GET':
        
        contri_Products = {
            'contribution': contribution,
            'category':Category.query.get(contribution.Category_id),
            'Products':Products,
           # 'numProds': len(Products),
            'participant':participant
        }
        return render_template('participant/detailed_recycle.html',contri_Products=contri_Products )
# ── Rewards ───────────────────────────────────────────────────────────────────

@participant.route('/rewards')
def rewards():
    user = get_user(current_user.id)
    return render_template("participant/rewards.html",
        user_points=user["points"],
        rewards=[
            {"id": 1, "name": "R50 Gift Card",   "description": "Redeemable at Pick n Pay.", "cost": 500, "icon": "🎁"},
            {"id": 2, "name": "Eco Tote Bag",    "description": "Reusable branded bag.",       "cost": 300, "icon": "🛍️"},
            {"id": 3, "name": "Tree Planted",    "description": "We plant a tree in your name.","cost": 200, "icon": "🌳"},
            {"id": 4, "name": "R20 Airtime",     "description": "Any SA network.",              "cost": 250, "icon": "📱"},
        ],
        redeemed=[
            {"name": "Eco Tote Bag", "date": "1 Mar 2026"},
        ],
    )

@participant.route('/redeem_reward', methods=['POST'])
def redeem_reward():
    reward_id = request.form.get('reward_id')
    return redirect(url_for('rewards'))

# ── Resources ─────────────────────────────────────────────────────────────────

@participant.route('/resources')
def resources():
    return render_template("participant/resources.html",
        resource_categories=[
            {
                "name": "Recycling Guides",
                "items": [
                    {"title": "What Can Be Recycled?", "url": "#",
                     "description": "A full guide to recyclable materials.", "type": "Guide"},
                    {"title": "How to Sort Waste",     "url": "#",
                     "description": "Step-by-step sorting instructions.",    "type": "Guide"},
                ],
            },
            {
                "name": "Tips & Tricks",
                "items": [
                    {"title": "10 Eco-Friendly Swaps", "url": "#",
                     "description": "Easy changes for a greener lifestyle.", "type": "Article"},
                    {"title": "Composting at Home",    "url": "#",
                     "description": "Turn food scraps into garden gold.",    "type": "Video"},
                ],
            },
            {
                "name": "Local Drop-off Points",
                "items": [
                    {"title": "Find a Recycling Centre Near You", "url": "#",
                     "description": "Locate your nearest recycling facility.", "type": "Map"},
                ],
            },
        ],
    )

# ── Updates ───────────────────────────────────────────────────────────────────

@participant.route('/updates')
def updates():
    return render_template("participant/updates.html",
        updates=[
            {"title": "New Recycling Initiative Launched!",
             "body":  "Wastewise has partnered with 50 local municipalities to expand collection points.",
             "date":  "12 Mar 2026", "tag": "New"},
            {"title": "Tips for Reducing Waste at Home",
             "body":  "Small changes in your daily routine can make a big difference.",
             "date":  "8 Mar 2026",  "tag": "Tip"},
            {"title": "March Challenge: Go Plastic-Free",
             "body":  "Join our monthly challenge and earn 100 bonus points.",
             "date":  "1 Mar 2026",  "tag": "Challenge"},
        ],
    )

# ── Referral ──────────────────────────────────────────────────────────────────

@participant.route('/referral')
def referral():
    return render_template("participant/referral.html",
        referral={
            "link":    "http://eco.com/ref/mbali",
            "count":   5,
            "points":  250,
            "pending": 2,
            "friends": [
                {"name": "Thabo M.",  "joined": "1 Mar 2026",  "status": "Active",  "points": 50},
                {"name": "Lerato K.", "joined": "15 Feb 2026", "status": "Active",  "points": 50},
                {"name": "Sipho N.",  "joined": "10 Feb 2026", "status": "Pending", "points": 0},
            ],
        },
    )

# ── Log item ──────────────────────────────────────────────────────────────────

@participant.route('/log_item', methods=['POST'])
@login_required
def log_item():
    participant = Participant.query.filter_by(user_id=current_user.id).first()
    categ= Category.query.get(int(request.form.get("Category_id")))
    contribution = Contribution(
        Participant_Id = participant.Participant_Id,
        user_id = current_user.id,
        Category_id= int(request.form.get("Category_id")),
        item_type = categ.Name,
        quantity  = request.form.get('quantity'),
        description  = request.form.get('description'),
    )
    
    db.session.add(contribution)
    
    db.session.commit()
    flash("Contribution logged susseccfully", "success")
    return redirect(url_for('/participant.history', user_id=current_user.id))



@participant.route('/add_EvidenceProduct/<int:contri_id>', methods=['POST'])
@login_required
def add_EvidenceProduct(contri_id):

    contribution= Contribution.query.get(contri_id)
    file = request.files.get("image")
    product = Product(
        contri_id=contribution.Contribution_Id,
        Product_Name = request.form.get('Product_Name'),
        Image=upload_Evidence_Image(file),
        decription= request.form.get("decription")
    )
    
    db.session.add(product)
    db.session.commit()
    
    flash("Prodcuct added successfully.", "success")
    return redirect(url_for('/participant.detailed_recycle', contri_id=contri_id))
    
 
@participant.route('/edit_EvidenceProduct/<int:prod_id>', methods=['POST'])   
@login_required
def edit_EvidenceProduct(prod_id):
    
    
    product = Product.query.get(prod_id)
    product.Product_Name = request.form.get('Product_Name'),
    product.Image=upload_Evidence_Image(request.files.get("image")),
    product.decription= request.form.get("decription")
    
    
def upload_Evidence_Image(file):

    if not file or file.filename == "":
        return None

    if file and allowed_file(file.filename):

        # Generate unique filename
        filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filename

