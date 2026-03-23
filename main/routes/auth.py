from flask import Blueprint, render_template, url_for, request, redirect, flash, flash
from main.models.auth import User, OTP
from main.models.participant import Participant
from main.routes.default import send_email
from main import db, bcrypt
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user
from getpass import getpass
import random
from datetime import datetime, timezone, timedelta
auth = Blueprint("/auth", __name__, url_prefix="/auth")

@auth.route("/signup", methods=['POST', 'GET'])
def signup():
    
   
        
    if  request.method == 'POST':
        try:
            if validatePassword(request.form.get('password'), request.form.get('password2')):
                new_user = User(
                    fname=request.form.get('first_name'),
                    lname=request.form.get('last_name'),
                    email=request.form.get('email').lower(),
                    is_terms_accepted = "is_terms_accepted" in request.form,
                    is_account_active = False,
                    password= bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
                )
                
                db.session.add(new_user)
                
                db.session.commit()
                flash(f'Account created successfully!', 'success')
                otp = OTP(new_user.id,generate_code(),'Pending')
                db.session.add(otp)
                db.session.commit()
                if send_otp(new_user,otp):
                    flash(f'OTP sent to "{new_user.email}" please visit your inbox', "success")
                    return redirect(url_for('/auth.confirm_otp', action="verify_email"))
                else:
                    flash(f"Somthing went wrong while sending OTP, please try again.", "danger")
                    return redirect(url_for('/auth.confirm_otp', action=""))
                    
                #return redirect(url_for('default.home'))
            else:
                flash(f'Password do not match, try login.','danger')
                return render_template("auth/signup.html", new_user=User(request.form['first_name'],request.form['last_name'],request.form['email'],''))
        
        except IntegrityError:
            flash(f'Username ({new_user.email}) already taken, try login.','danger')
            return render_template("auth/signup.html", new_user=new_user)
    else:
        
        
        return render_template("auth/signup.html", new_user=User('','','',''))
        
  
@auth.route("/login", methods=['GET', 'POST'])
def login():
    
    if request.method == 'GET':
        
        return render_template('auth/login.html')
    elif request.method == 'POST':
        
        email = request.form.get('email').lower()
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            if bcrypt.check_password_hash(user.password, password) and user.is_account_active:
            
                if user.is_account_active == False:
                    flash("You need to activate your account by confirming your email.", "danger")
                    otp = OTP(user.id,generate_code(),'Pending')
                    db.session.add(otp)
                    db.session.commit()
                    
                    if send_otp(user,otp):
                        flash(f'OTP sent to "{user.email}" please visit your inbox', "success")
                        return redirect(url_for('/auth.confirm_otp', action="verify_email"))
                    else:
                        flash(f"Somthing went wrong while sending OTP, please try again.", "danger")
                        return redirect(url_for('/auth.confirm_otp'))
                else:   
            
                    login_user(user)
                    if user.is_superuser == True:
                        return redirect(url_for('/admin.dashboard'))
                    else:
                        if checkProfile(user.id):
                            return redirect(url_for('/participant.dashboard'))
                        else:
                            flash("Complete your profile.", "danger")
                            return redirect(url_for('/auth.account', id=user.id))
        
            else:
                
                flash("Invalid login details","danger" )
                return redirect(url_for("/auth.login"))
        else:
            
            flash(f"No user found matching email: {email}")
            return redirect(url_for("/auth.login"))

    
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('default.home'))
    
    
@auth.route("/account/<int:id>", methods=['GET', 'POST'])
@login_required
def account(id):
    
    if id:
        user = User.query.get(int(id))
    elif current_user.is_authenticated:
        user = current_user
    else:
        flash("User account not found!", "danger")
        return redirect(url_for('default.home'))
    
    if request.method == 'GET':
        profile ={
            "participant": getParticipant(user.id),
            "user":user
        }
         
        return render_template('auth/account.html', profile=profile)
    elif request.method == 'POST':
        
        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.email = request.form["email"]
        
        try:
            user.is_staff  = "is_staff" in request.form
            user.is_superuser = "is_superuser" in request.form
        except:
             pass
         
         
        participant = getParticipant(user.id)
        if not participant:
            participant = Participant(
                user_id= user.id,
                PhoneNumber= request.form.get('PhoneNumber'),
                PhysicalAddress= request.form.get('PhysicalAddress'),
                
            )
            db.session.add(participant)
        else:
            participant.PhoneNumber= request.form["PhoneNumber"]
            participant.PhysicalAddress= request.form["PhysicalAddress"]
            
        db.session.commit()
        
        flash("Changes saved successfully!", 'success')
        
        if current_user.is_superuser:
            return redirect(url_for('/auth.users'))
        else:
            return redirect(url_for('/auth.account', id=user.id))
        
@auth.route("/change_password/<int:id>",methods=['GET','POST'])
@login_required
def change_password(id):
    
    user = User.query.get(int(id))
    if request.method =='POST':
        
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        new_password2 = request.form["new_password2"]
        
        if bcrypt.check_password_hash(user.password, old_password):
            if new_password == new_password2:
                user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
                db.session.commit()
                flash("Password updated successfully!", 'success')
                return redirect(url_for('/auth.account',id=user.id))
            else:
                flash(f'new password do not match, try login.','danger')
                return redirect(url_for('/auth.change_password', id=id))
        else:
            flash(f'Old password invalid, try login.','danger')
            return redirect(url_for('/auth.change_password', id=id))
    else:
        return render_template('auth/change_password.html', user=user)


@auth.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    
    if request.method == 'POST':
        
        email = request.form.get("email").lower()
        user = User.query.filter_by(email=email).first()
        if user:
            otp = OTP(user.id,generate_code(),'Pending')
            db.session.add(otp)
            db.session.commit()
            if send_otp(user, otp):
                
                flash(f"OTP sent to '{user.email}', please access your email inbox.", "success")
                return redirect(url_for('/auth.confirm_otp',  action="reset_password"))
                
            else:
                flash(f"Something went wrong while sending OTP sent to '{user.email}', Please try again", "danger")
                return redirect(url_for('/auth.reset_request'))
                
            
        else:
            flash(f"No user found matching: {email}", "danger")
            return redirect(url_for('/auth.reset_request'))
            pass
    elif request.method == 'GET':
        return render_template('auth/reset_password_request.html')
    
@auth.route('/confirm_otp/<action>', methods=['POST', 'GET'])
def confirm_otp(action):
    
    if request.method == 'GET':
        
        return render_template('auth/confirm_otp.html', action=action)
    elif request.method == 'POST':
        
        otpcode = request.form.get('otpcode')
        otp_obj = OTP.query.filter_by(code=otpcode, status="Pending").first()
        
        if otp_obj.status == "Pending":
            
           
                       
    
            user = User.query.get(otp_obj.user_id)
            user.is_account_active = True
            db.session.commit()
            
            logout_user()
            if action == 'reset_password':
                
                return redirect(url_for('auth.reset_password'))
            elif action == 'verify_email':
                flash("Email verified successfully. You may login", "success" )
                return redirect(url_for('/auth.account', id=user.id))
        else:
                    
            flash("OTP expired, we send a new one", "danger")
            otp_obj.status = 'Expired'
            otp = OTP(user.id,generate_code(),'Pending')
            db.session.add(otp)
            db.session.commit()
            if send_otp(user, otp):
                
                flash(f"OTP sent to '{user.email}', please access your email inbox.", "success")
                return redirect(url_for('/auth.confirm_otp',  action="reset_password"))
                
            else:
                flash(f"Something went wrong while sending OTP sent to '{user.email}', Please try again", "danger")
                return redirect(url_for('/auth.confirm_otp',  action="reset_password"))
        
@auth.route('/reset_password/<int:user_id>', methods=['POST', 'GET'])
def reset_password(user_id):
    
    if request.method == 'GET':
        
        return render_template('auth/reset_password.html')
    elif request.method == 'POST':
        pass
        
        
        
        
def send_otp(user, otp):
    subject = 'OTP: Confirm email'
    msg = f'Dear {user.first_name}\n'
    msg+=f'Please use the code below to comfirm your email address.\n'
    msg += f'OTP: {otp.code}\n'
    msg += f'\n'
    msg += f'Kind regards,\nWastwise'
    
    return send_email(user.email,subject, msg)
    
   

def generate_code():
    return str(random.randint(100000, 999999))




#Admin

@auth.route("/users", methods=['GET'])
@login_required
def users():
    
    users = User.query.all()
    return render_template('auth/users.html', users=users)


def createsuperuser():
    try:
        fname = input("Enter first name: ")
        lname = input("Enter Last name: ")
        email = input("Enter email address: ").lower()
        password = getValidatePassword()
        
        
        new_user = User(
            fname=fname,
            lname=lname,
            email=email,
            password= bcrypt.generate_password_hash(password).decode('utf-8'),
            is_staff = True,
            is_superuser = True,
            is_terms_accepted = True,
            is_account_active = True
            
        )
        
        db.session.add(new_user)
        db.session.commit()
        print(f'user({new_user.email}) account created successfully!')
    except KeyboardInterrupt:
        print("\n\nExited!")
    except IntegrityError:
        print(f"Username({email}) is already taken")  
        
   
            
    
    
def getValidatePassword():
    password1 = getpass("Enter email new password: ")
    password2 = getpass("Re-Enter email new password: ")
    
    if password1 != password2:
        print("Password do not match!")
        print("_______________________")
        getValidatePassword()
    else:
        return password1
    
    
def validatePassword(password1,password2):
    
    if password1 != password2:
        return False
    else:
        return password1
    
    
    
def checkProfile(user_id):
    
    user = User.query.get(user_id)
    if Participant.query.filter_by(user_id = user.id).first():
        return True
    else:
        return False
    
def getParticipant(user_id):
    user = User.query.get(user_id)
    return Participant.query.filter_by(user_id = user.id).first()
    
    