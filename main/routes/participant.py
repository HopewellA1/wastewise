from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from main.models.participant import Contribution, Participant
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