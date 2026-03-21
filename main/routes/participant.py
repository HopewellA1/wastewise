from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from main.models.participant import Participant
from main.models.auth import User
from main import db


    
    
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



@participant.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template("participant/dashboard.html",
        user=get_user(),
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



def get_user():
    return {"name": "Mbali", "points": 720, "rank": 4}


def get_leaderboard():
    return [
        {"username": "Alice",  "points": 1200},
        {"username": "Bob",    "points": 950},
        {"username": "Carol",  "points": 800},
        {"username": "Mbali",  "points": 720},
        {"username": "David",  "points": 610},
    ]




# ── Leaderboard ───────────────────────────────────────────────────────────────

@participant.route('/leaderboard')
def leaderboard():
    user = get_user()
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

@participant.route('/history')
def history():
    return render_template("participant/history.html",
        history=[
            {"type": "Plastic Bottles", "quantity": 5,  "date": "12 Mar 2026", "points": 50},
            {"type": "Paper",           "quantity": 10, "date": "10 Mar 2026", "points": 30},
            {"type": "Glass",           "quantity": 2,  "date": "8 Mar 2026",  "points": 20},
            {"type": "Metal Cans",      "quantity": 3,  "date": "5 Mar 2026",  "points": 30},
        ],
    )

# ── Rewards ───────────────────────────────────────────────────────────────────

@participant.route('/rewards')
def rewards():
    user = get_user()
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
def log_item():
    item_type = request.form.get('item_type')
    quantity  = request.form.get('quantity')
    return redirect(url_for('history'))

