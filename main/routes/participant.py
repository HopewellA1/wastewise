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