import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from main.models.participant import Category, Contribution, Participant,Reward
from main.models.auth import User
from main.routes.default import send_email
from main import db
from dotenv import load_dotenv
from openai import OpenAI
import random
load_dotenv()
from main import db, allowed_file, UPLOAD_FOLDER




admin = Blueprint("/admin", __name__, url_prefix="/admin")



@admin.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    
    
    return render_template('admin/dashboard.html')


@admin.route("/Categories", methods=['GET', 'POST'])
@login_required
def Categories():
    
    if request.method == 'GET':
        categories = list()
        dbCategories = Category.query.all()
        
        for category in dbCategories:
            
            categories.append(
                {
                    "category": category,
                    "admin_user": User.query.get(category.user_id)
                }
            )
        
        return render_template('admin/Categories.html', categories = categories)
    
@admin.route("/new_category", methods=['POST', 'GET'])
@login_required
def new_category():
 
    if request.method == 'POST':
        
        categ = Category(
            user_id = current_user.id,
            Name = request.form.get("Name")
        )
        db.session.add(categ)
        db.session.commit()
        flash("Category added successfully", "success")
        
        return redirect(url_for('/admin.Categories'))
    
@admin.route('/edit_category/<int:categ_id>', methods=["POST"])
@login_required
def edit_category(categ_id):
    
    category = Category.query.get(categ_id)
    category.Name = request.form.get("Name")
    db.session.commit()
    flash("Changes saved successfully.", "success")
    return redirect(url_for('/admin.Categories'))

@admin.route('/delete_category/<int:categ_id>', methods=["POST"])
@login_required
def delete_category(categ_id):
    
    category = Category.query.get(categ_id)
    category.Name = request.form.get("Name")
    try:
        
        db.session.delete(category)
        db.session.commit()
        flash("Categry delted!", "danger")
    except:
        flash("This categiry has been contrubuted on, for data Integrity the action has been aborted!", "danger")
    return redirect(url_for('/admin.Categories'))


@admin.route('/submissions/<filter>', methods=['GET', 'POST'])
@login_required
def submissions(filter):
    
    if filter== 'all':
        contributions = Contribution.query.all().order_by(Contribution.Contribution_Id.desc()).all()
    elif filter == 'history':
        contributions = Contribution.query.filter_by(is_history =True).order_by(Contribution.Contribution_Id.desc()).all()
    else:
        contributions = Contribution.query.filter_by(status =filter).order_by(Contribution.Contribution_Id.desc()).all()   
    subs = list()
    
    for contri_ in contributions:
        
        user = User.query.get(Participant.query.get(contri_.Participant_Id).user_id)
        wastType = Category.query.get(contri_.Category_id)
        subs.append(
            {
                'contri_': contri_,
                "user": user,
                "username": user.first_name +'_'+ user.last_name[0],
                "categ": wastType,
               
            }
            
        )  
        
    return render_template('admin/submissions.html', subs=subs,  filter=filter) 
        
    
    
@admin.route('/approve_submission/<int:contri_id>', methods=[ 'POST'])
@login_required
def approve_submission(contri_id):
    
    contribution = Contribution.query.get(contri_id)
    
    contribution.status = "Approved"
    contribution.is_history = True
    contribution.points_awarded = int(request.form.get('points'))
    contribution.rating = int(request.form.get("rating"))
    participant = Participant.query.get(contribution.Participant_Id)
    participant.total_points_accumulated +=  int(request.form.get('points'))
    participant.points += int(request.form.get('points'))
    
    
    
    db.session.commit()
    approve_mail(contri_id)
    flash("submision approved successfully", "success")
    return redirect(url_for('/admin.submissions', filter=contribution.status))
    
    
@admin.route('/decline_submission/<int:contri_id>', methods=[ 'POST'])
@login_required
def decline_submission(contri_id):
    
    contribution = Contribution.query.get(contri_id)
    contribution.status = "Declined"
    contribution.is_history = True
    db.session.commit()
    declin_mail(contri_id, request.form.get('DeclineReason'))
    flash("submision declined ", "danger")
    return redirect(url_for('/admin.submissions', filter=contribution.status))
    
            
        
def approve_mail(contri_id):
    
    
    subject = 'Submission approved'
    
    contribution = Contribution.query.get(contri_id)
    participant = Participant.query.get(contribution.Participant_Id)
    categ = Category.query.get(contribution.Category_id)
    user = User.query.get(participant.user_id)

    
    body='Dear '+ user.first_name + ' '+ user.last_name
    body+= '\nWe are delighted to inform you that your submission has been approved.'
    body+= f'\nFor all the greate work you have been awarded {contribution.points_awarded} points\n'
    body+= f'Message from us:\n'
    body +=generate_appreciation_message()
    body += "\n\nKind regards,\nWastwise"
    
    return send_email(user.email, subject,body )
    
    
def declin_mail(contri_id, reason):
    
    
    subject = 'Submission Status'
    
    contribution = Contribution.query.get(contri_id)
    participant = Participant.query.get(contribution.Participant_Id)
    categ = Category.query.get(contribution.Category_id)
    user = User.query.get(participant.user_id)
    body='Dear '+ user.first_name + ' '+ user.last_name
    body+= '\nWe regret to inform you that your submission has been declined, due to reason stated below.'
    body+= f'{reason}\n'
    body+= f'_____________________________________________________\n\n'
    body+= f'Message from us:\n'
    body +=generate_appreciation_message()
    body += "\n\nKind regards,\nWastwise"
    
    return send_email(user.email, subject,body )
    
    
    
    
    
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
    
    
     
#Reward admin actions********************************************************************************************************

@admin.route('/rewards', methods=['GET'])
@login_required
def rewards():
    
    wards = Reward.query.all()
    for w in wards:
        w.category = 'Voucher'
        
    db.session.commit()
    totalRewards = count(wards)
    
    return render_template('admin/rewards.html', rewards=wards, totalRewards=totalRewards)


@admin.route('/New_reward', methods=['POST'])
@login_required
def New_reward():
    
    reward = Reward(
        reward_name= request.form.get('reward_name'),
        points_required= int(request.form.get('points_required')),
        description= request.form.get('description'),
        quantity= int(request.form.get('quantity')),
        Reward_Icone= upload_Reward_Icon(request.files.get("Reward_Icone")),
        user_id=current_user.id,
        Reward_Category= request.form.get('Reward_Category')
        
    )
    
    db.session.add(reward)
    
    db.session.commit()
    
    flash("New reward added successfully", "success")
    
    return redirect(url_for('/admin.rewards'))


@admin.route('/edit_reward/<int:reward_id>', methods=['POST'])
@login_required
def edit_reward(reward_id):
    
    reward = Reward.query.get(reward_id)
    
    reward.reward_name= request.form.get('reward_name')
    reward.points_required= int(request.form.get('points_required'))
    reward.description = request.form.get('description')
    reward.quantity = int(request.form.get('quantity'))
    file = request.files.get("Reward_Icone")
    reward.Reward_Category = request.form.get('Reward_Category')
    if file:
        reward.Reward_Icone= upload_Reward_Icon(file)
    try:
        reward.is_available  = "is_available" in request.form
    except:
            pass

    db.session.commit()
    
    flash('Reward added successfully', "success")
    return redirect(url_for('/admin.rewards'))


@admin.route('/delete_reward/<int:reward_id>', methods=['POST', 'GET'])
@login_required
def delete_reward(reward_id):
    
    reward = Reward.query.get(reward_id)
    db.session.delete(reward)
    db.session.commit()
    flash("Reward deleted", "danger")
    return redirect(url_for('/admin.rewards'))
    
def upload_Reward_Icon(file):

    if not file or file.filename == "":
        return None

    if file and allowed_file(file.filename):

        # Generate unique filename
        filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filename



def count(list_item):
    numitems = int()
    for item in list(list_item):
        numitems += 1
    return numitems