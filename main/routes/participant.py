import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, url_for, request, redirect, flash,jsonify,current_app
from flask_login import login_user, logout_user, login_required, current_user
from main.models.participant import Contribution, Participant,Category, Product, Reward, ParticipantReward
from main.models.auth import User
from datetime import date, datetime, timezone
from main.routes.default import send_email
import random
import string
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from email.message import EmailMessage
import smtplib
from main import mail, getEmailCreds
import qrcode


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
@login_required
def dashboard():
    return render_template("participant/dashboard.html",
        user=get_user(current_user.id),
        leaderboard=get_leaderboard()[:3],
        challenges=[
            {"title": "Plastic Challenge", "progress": 70},
            {"title": "Weekly Goal",        "progress": 50},
        ],
        history=gethistory(current_user.id),
        referral={"link": "http://eco.com/ref/mbali", "count": 5, "points": 250},
        rewards=[{"name": "Gift Card", "description": "R50 voucher"}],
        resources=[{"title": "Eco Tips", "url": "http://eco.com/tips"}],
        updates=["New Recycling Initiative Launched!", "Tips for Reducing Waste at Home"],
    )

def gethistory(userId):
    
    participant = Participant.query.get(user_id =userId )
    contires = Contribution.query.filter_by(Participant_Id = participant.Participant_Id).all()
    partReward = ParticipantReward.query.filter_by(Participant_Id = participant.Participant_Id).all()
    hist = []
    for contri in partReward:
        reward = Reward.query.get(contri.Reward_Id)
        hist.append({
            "type":reward.reward_name,
            "date":contri.date_claimed.date(),
            "points":contri.points_required
            
        })

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
@login_required
def rewards():
    
    
    
    user = current_user
    participant = Participant.query.filter_by(user_id = user.id).first()
    rewards = Reward.query.all()
    print("rewards: ", rewards)
    redeemed_rewards = getRedeemedRewards(participant.Participant_Id) #[{"name": "Eco Tote Bag", "date": "1 Mar 2026"},]
    return render_template("participant/rewards.html",user_points=participant.points,rewards=rewards, redeemed=redeemed_rewards )
    
def getRedeemedRewards(part_id):
    participant = Participant.query.get(part_id)
    redeemed_rewards = ParticipantReward.query.filter_by(Participant_Id = participant.Participant_Id).all()
    
    rewards = list()
    
    for reward in redeemed_rewards:
        rw = Reward.query.get(reward.Reward_Id)
        rewards.append({
            "name": rw.reward_name,
            "date":reward.date_claimed.date(),
            "points":rw.points_required
        })
    return rewards   
# [
#     {"id": 1, "name": "R50 Gift Card",   "description": "Redeemable at Pick n Pay.", "cost": 500, "icon": "🎁"},
#     {"id": 2, "name": "Eco Tote Bag",    "description": "Reusable branded bag.",       "cost": 300, "icon": "🛍️"},
#     {"id": 3, "name": "Tree Planted",    "description": "We plant a tree in your name.","cost": 200, "icon": "🌳"},
#     {"id": 4, "name": "R20 Airtime",     "description": "Any SA network.",              "cost": 250, "icon": "📱"},
# ],

@participant.route('/redeem_reward/<int:reward_id>', methods=['POST'])
def redeem_reward(reward_id):
    reward = Reward.query.get(reward_id)
    participant = Participant.query.filter_by(user_id=current_user.id).first()
    participant.points -= reward.points_required
    
    partReward = ParticipantReward(
        Reward_Id=reward.Reward_Id,
        Participant_Id=participant.Participant_Id,
        points_used=reward.points_required,
        balancePoints=participant.points,
    )
    
    db.session.add(partReward)
    db.session.commit()
    if reward.Reward_Category == 'Event':
        deliverReward(partReward.ParticipantReward_ID) #for event
    elif reward.Reward_Category =='Voucher':
        
        print("on deliver")
        deliverVoucherReward(partReward.ParticipantReward_ID)
             
    
    flash(f"Reward redeemed successfully, {reward.points_required} points used.","success")
    
    return redirect(url_for('/participant.rewards'))

def deliverReward(partReward_id):
    
    partReward = ParticipantReward.query.get(partReward_id)
    reward = Reward.query.get(partReward.Reward_Id)
    participant = Participant.query.get(partReward.Participant_Id)
    user = User.query.get(participant.user_id)
    msg = EmailMessage()
    msg['subject'] = 'Reward redeemed'
    msg['From'] = getEmailCreds()["sender_email"]
    msg['To'] = user.email
    msg.set_content(generate_appreciation_message())
    
    ticket_buffer = generate_ticket_buffer(
        reward.reward_name,
        user.email,
        generate_voucher_code(),
        partReward.date_claimed.date(),
        os.path.join(
        current_app.root_path,
        'static',
        'uploads',
        reward.Reward_Icone
)
    )
    msg.add_attachment(
        ticket_buffer.read(),
        maintype='image',
        subtype='png',
        filename=f'{user.first_name}_{reward.reward_name}.png'
    )
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(f"{getEmailCreds()["sender_email"]}", f"{getEmailCreds()["app_password"]}")
        smtp.send_message(msg)
    
def deliverVoucherReward(partReward_id):
    partReward = ParticipantReward.query.get(partReward_id)
    reward = Reward.query.get(partReward.Reward_Id)
    participant = Participant.query.get(partReward.Participant_Id)
    user= User.query.get(participant.user_id)
    Subject = f'Your {reward.reward_name} Has Been Issued!'
    body = f'Hi {user.first_name},\n Well done! \n\nYou have redeemed your {reward.reward_name} successfully.'
    body +=f'\nReward: {reward.reward_name}'
    body +=f'\nPoints Used: {reward.points_required}'
    body +=f'\nVoucher Code: {str(generate_voucher_code())}'
    #body +=f'\n\n{generate_appreciation_message()}'
    body += '\n\nKind regards,\nWasteWise'
    
    send_email(user.email, Subject,body)
     
    
def generate_ticket_buffer(event_name,user_name,ticket_code,event_date,image_path):
    WIDTH = 400
    HEIGHT = 550
    TOP_HEIGHT = 280  
    BOTTOM_HEIGHT = HEIGHT - TOP_HEIGHT

   
    poster = Image.open(image_path).convert("RGB")
    poster = poster.resize((WIDTH, TOP_HEIGHT))

    #clean white tictete creation
    ticket = Image.new("RGB", (WIDTH, HEIGHT), "white")

    # Paste poster at top of the ticket above
    ticket.paste(poster, (0, 0))

    draw = ImageDraw.Draw(ticket)

    # Draw divider (dashed line )
    for x in range(0, WIDTH, 20):
        draw.line([(x, TOP_HEIGHT), (x + 10, TOP_HEIGHT)], fill=(150, 150, 150), width=2)

    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        text_font = ImageFont.truetype("arial.ttf", 20)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # Bottom section text (clean layout)
    y_start = TOP_HEIGHT + 20

    draw.text((30, y_start), event_name, font=title_font, fill=(0, 0, 0))
    draw.text((30, y_start + 50), f"Email: {user_name}", font=text_font, fill=(50, 50, 50))
    draw.text((30, y_start + 90), f"Issue Date: {event_date}", font=text_font, fill=(50, 50, 50))

    #QR code adding
    qr = qrcode.make(ticket_code)
    qr = qr.resize((120, 120))

    qr_x = WIDTH - 150
    qr_y = HEIGHT - 160

    ticket.paste(qr, (qr_x, qr_y))

    #Tictet code 
    draw.text(
        (qr_x, qr_y + 125),
        ticket_code,
        font=text_font,
        fill=(0, 120, 80)
    )


    # Border (subtle)
    draw.rectangle([(0, 0), (WIDTH-1, HEIGHT-1)], outline=(200, 200, 200), width=2)

    # Saving to buffer
    buffer = BytesIO()
    ticket.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

 
    
def generate_voucher_code(length=10):
    return ''.join(random.choice(string.digits) for _ in range(length))
    

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
    return redirect(url_for('/participant.detailed_recycle', contri_id=contribution.Contribution_Id))

#detailed_recycle(contri_id)

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
    file = request.files.get("image")
    image = upload_Evidence_Image(file)
    if image is not None:
        product.Image=image
        
    product.decription= request.form.get("decription")
    product = Product.query.get(prod_id)
    
    product.Product_Name = request.form.get('Product_Name')
    
    db.session.commit()
    flash("Changes saved successfully","success")
    return redirect(url_for('/participant.detailed_recycle', contri_id=product.Contribution_Id))
    
   
@participant.route('/delete_EvidenceProduct/<int:prod_id>', methods=['POST'])   
@login_required
def delete_EvidenceProduct(prod_id):
    product = Product.query.get(prod_id)
    contri_id=product.Contribution_Id
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted","danger")
    return redirect(url_for('/participant.detailed_recycle', contri_id=contri_id))
    
    
    
def upload_Evidence_Image(file):

    if not file or file.filename == "":
        return None

    if file and allowed_file(file.filename):

        # Generate unique filename
        filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filename
    flash("File type not allowed", "danger")



@participant.route('/submit_contribution/<int:contri_id>',methods=['POST'] )
@login_required
def submit_contribution(contri_id):
    
    contri_ = Contribution.query.get(contri_id)
    contri_.status = "Pending"
    contri_.timestamp =  datetime.now(timezone.utc)
    db.session.commit()
    new_contri_AdminAlert(contri_id)
    return redirect(url_for('/participant.history',user_id= current_user.id))
    
    #notify admins
@participant.route('/cancel_submission/<int:contri_id>',methods=['POST'] )
@login_required
def cancel_submission(contri_id):
    
    contribution = Contribution.query.get(contri_id)
    contribution.status = "Cenceled"
    contribution.is_history = True
    participant = Participant.query.get(contribution.Participant_Id)
    db.session.commit()
    flash("submision canceled successfully", "success")
    return redirect(url_for('/participant.history',user_id= current_user.id))
    
        

def new_contri_AdminAlert(contri_id):
    from main.routes.default import send_email
    contri_ = Contribution.query.get(contri_id)
    participant = Participant.query.get(contri_.Participant_Id)
    partuser= User.query.get(participant.user_id)
    superusers = User.query.filter_by(is_superuser=True).all()
  
    numSent = int()
    for user in superusers:
        message = superuserEmailmessage(participant,user, contri_)
        print("message:" ,message)
        if send_email(user.email,message["Subject"],message["body"]):
            numSent +=1
            
    if numSent > 0:
        flash("Recycle contribution submitted successfully, admin has been notfied", "success")
    else:
        flash("Recycle contribution submitted successfully, Something went wrong while notifiying the admin", "info")
            
    
        
        
        



def superuserEmailmessage(participant, superuser, contri_):
    
    partUser = User.query.get(participant.user_id)

    Subject =  'New Contribution Submitted for Approval'
    
    body = f'Dear {superuser.first_name},\n\nA new contribution has been submitted and is awaiting your review.\n'
    body += f'Participant Details:\nNeme: {partUser.first_name}\nPhone Number: {participant.PhoneNumber}\n\n'
    body += f'Contribution Details:\nDescription: {contri_.description}\nSubmitted at: {contri_.timestamp}\n'
    body += 'Please log in to the system to review and approve or reject this contribution.\n\n'
    body += 'Kind regards,\n'
    body += 'WasteWise System'
    
    return {
        'Subject': Subject,
        "body": body
    }
    
    
    
    
@participant.route('/api/get-points/<int:user_id>', methods=['GET'])
@login_required
def get_points(user_id):
    
    participant = Participant.query.filter_by(user_id = user_id).first()
    
    return jsonify({
        "points":participant.points
    })







def generate_appreciation_message():
        
    APPRECIATION_MESSAGES = [
        "Thank you for making a difference and contributing to a cleaner future 🌍",
        "Your effort today helps build a better tomorrow. Keep going!",
        "We appreciate your commitment to keeping the environment clean 💚",
        "Every piece of waste you collect brings us closer to a greener world",
        "Your contribution truly matters — thank you for stepping up!",
        "You are part of the solution. Thank you for caring!",
        "Together we can create a sustainable future — thank you!",
        "Your actions inspire positive change in the community",
        "Thank you for protecting our planet through your efforts",
        "Cleaner streets, brighter future — thanks to you!",
        
        "Your dedication to recycling is making a real impact",
        "Thank you for turning waste into opportunity ♻️",
        "Small actions like yours lead to big environmental change",
        "We see your effort and we appreciate you!",
        "You are helping create a healthier environment for all",
        "Thank you for choosing to make a difference today",
        "Your contribution is a step toward sustainability",
        "You are helping reduce waste and protect nature 🌱",
        "Every contribution counts — and yours matters!",
        "Thank you for being environmentally responsible",
        
        "You are a champion for a cleaner planet!",
        "Your effort is helping build a waste-free future",
        "We appreciate your positive impact on the environment",
        "Thank you for doing your part in recycling and sustainability",
        "You are helping transform waste into valuable resources",
        "Your commitment does not go unnoticed — thank you!",
        "Together we are making the world a better place",
        "Thank you for being part of the recycling movement",
        "Your actions today will benefit future generations",
        "Keep up the great work — we appreciate you!",
        
        "Thank you for contributing to a greener tomorrow",
        "Your effort is inspiring change in your community",
        "You are helping reduce pollution — thank you!",
        "Your contribution helps keep our environment safe",
        "We value your commitment to sustainability",
        "Thank you for helping us build a cleaner world",
        "You are making a real difference — thank you!",
        "Your recycling effort is powerful and meaningful",
        "We appreciate your dedication to environmental care",
        "Thank you for taking action for the planet 🌍",
        
        "Your work helps turn waste into something useful",
        "Thank you for being part of the solution",
        "Your contribution brings us closer to a sustainable future",
        "We are grateful for your environmental efforts",
        "Thank you for helping reduce environmental impact",
        "Your actions support a cleaner and greener community",
        "You are making sustainability a reality",
        "Thank you for your valuable contribution today",
        "Your effort helps protect our natural resources",
        "Together we are building a better tomorrow"
    ]
    return random.choice(APPRECIATION_MESSAGES)
    