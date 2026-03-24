from flask import Blueprint, render_template, url_for, request, redirect, flash
from main.models.auth import User, OTP
from main.models.participant import Participant
from main.routes.default import send_email
from main import db, bcrypt
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user
from getpass import getpass
import random
import requests
from datetime import datetime, timezone, timedelta
import os

auth = Blueprint("/auth", __name__, url_prefix="/auth")

# reCAPTCHA configuration
RECAPTCHA_SECRET_KEY = "6LcGQ5UsAAAAAGL0rPj_gfpoLpmbI7GqtgNYuzjd"
RECAPTCHA_SITE_KEY = "6LcGQ5UsAAAAAKtRoGICj5w881lDvDt7q9i7FUiL"

@auth.route("/signup", methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        try:
            # Verify reCAPTCHA
            recaptcha_response = request.form.get('g-recaptcha-response')
            
            if not recaptcha_response:
                flash('Please complete the reCAPTCHA verification.', 'danger')
                return render_template("auth/signup.html", new_user=User(request.form.get('first_name', ''), request.form.get('last_name', ''), request.form.get('email', ''), ''), recaptcha_site_key=RECAPTCHA_SITE_KEY)
            
            # Verify with Google
            verification_data = {
                'secret': RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            
            try:
                verification_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=verification_data, timeout=10)
                verification_result = verification_response.json()
                
                if not verification_result.get('success', False):
                    flash('reCAPTCHA verification failed. Please try again.', 'danger')
                    return render_template("auth/signup.html", new_user=User(request.form.get('first_name', ''), request.form.get('last_name', ''), request.form.get('email', ''), ''), recaptcha_site_key=RECAPTCHA_SITE_KEY)
                    
            except requests.RequestException:
                flash('Error verifying reCAPTCHA. Please try again.', 'danger')
                return render_template("auth/signup.html", new_user=User(request.form.get('first_name', ''), request.form.get('last_name', ''), request.form.get('email', ''), ''), recaptcha_site_key=RECAPTCHA_SITE_KEY)
            
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
                otp = OTP(new_user.id, generate_code(), 'Pending')
                db.session.add(otp)
                db.session.commit()
                if send_otp(new_user, otp):
                    flash(f'OTP sent to "{new_user.email}" please visit your inbox', "success")
                    return redirect(url_for('/auth.confirm_otp', action="verify_email"))
                else:
                    flash(f"Something went wrong while sending OTP, please try again.", "danger")
                    return redirect(url_for('/auth.confirm_otp', action=""))
                    
            else:
                flash(f'Password do not match, try login.','danger')
                return render_template("auth/signup.html", new_user=User(request.form.get('first_name', ''), request.form.get('last_name', ''), request.form.get('email', ''), ''), recaptcha_site_key=RECAPTCHA_SITE_KEY)
        
        except IntegrityError:
            flash(f'Username ({new_user.email}) already taken, try login.','danger')
            return render_template("auth/signup.html", new_user=new_user, recaptcha_site_key=RECAPTCHA_SITE_KEY)
    else:
        return render_template("auth/signup.html", new_user=User('','','',''), recaptcha_site_key=RECAPTCHA_SITE_KEY)
        
  
@auth.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        # ✅ IMPORTANT: Pass site key to template
        return render_template(
            'auth/login.html',
            recaptcha_site_key=RECAPTCHA_SITE_KEY
        )

    elif request.method == 'POST':

        # ✅ STEP 1: Get reCAPTCHA response
        recaptcha_response = request.form.get('g-recaptcha-response')

        if not recaptcha_response:
            flash('Please complete the reCAPTCHA verification.', 'danger')
            return redirect(url_for("/auth.login"))

        # ✅ STEP 2: Verify with Google
        verification_data = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }

        try:
            verification_response = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data=verification_data,
                timeout=10
            )
            verification_result = verification_response.json()

            if not verification_result.get('success'):
                flash('reCAPTCHA verification failed. Please try again.', 'danger')
                return redirect(url_for("/auth.login"))

        except requests.RequestException:
            flash('Error verifying reCAPTCHA. Please try again.', 'danger')
            return redirect(url_for("/auth.login"))

        # ✅ STEP 3: Continue login logic
        email = request.form.get('email').lower()
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            if bcrypt.check_password_hash(user.password, password):

                if user.is_account_active == False:
                    flash("You need to activate your account by confirming your email.", "danger")

                    otp = OTP(user.id, generate_code(), 'Pending')
                    db.session.add(otp)
                    db.session.commit()

                    if send_otp(user, otp):
                        flash(f'OTP sent to "{user.email}" please visit your inbox', "success")
                        return redirect(url_for('/auth.confirm_otp', action="verify_email"))
                    else:
                        flash("Something went wrong while sending OTP, please try again.", "danger")
                        return redirect(url_for('/auth.confirm_otp'))

                else:
                    login_user(user)

                    if user.is_superuser:
                        return redirect(url_for('/admin.dashboard'))
                    else:
                        if checkProfile(user.id):
                            return redirect(url_for('/participant.dashboard'))
                        else:
                            flash("Complete your profile.", "danger")
                            return redirect(url_for('/auth.account', id=user.id))

            else:
                flash("Invalid login details", "danger")
                return redirect(url_for("/auth.login"))

        else:
            flash(f"No user found matching email: {email}", "danger")
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
            otp = OTP(user.id, generate_code(), 'Pending')
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
        
        if otp_obj and otp_obj.status == "Pending":
            
            # Check if OTP is expired (older than 10 minutes)
            if otp_obj.created_at and datetime.now(timezone.utc) - otp_obj.created_at > timedelta(minutes=10):
                flash("OTP expired. Please request a new one.", "danger")
                otp_obj.status = 'Expired'
                db.session.commit()
                return redirect(url_for('/auth.reset_request'))
            
            user = User.query.get(otp_obj.user_id)
            user.is_account_active = True
            otp_obj.status = 'Used'
            db.session.commit()
            
            logout_user()
            if action == 'reset_password':
                return redirect(url_for('auth.reset_password', user_id=user.id))
            elif action == 'verify_email':
                flash("Email verified successfully. You may login", "success" )
                return redirect(url_for('/auth.login'))
        else:
                    
            flash("Invalid or expired OTP. Please request a new one.", "danger")
            return redirect(url_for('/auth.reset_request'))
        
@auth.route('/reset_password/<int:user_id>', methods=['POST', 'GET'])
def reset_password(user_id):
    
    if request.method == 'GET':
        
        return render_template('auth/reset_password.html', user_id=user_id)
    elif request.method == 'POST':
        
        password = request.form.get('password')
        password2 = request.form.get('password2')
        
        if password == password2:
            user = User.query.get(user_id)
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.commit()
            flash("Password has been reset successfully. You may now login.", "success")
            return redirect(url_for('/auth.login'))
        else:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('auth.reset_password', user_id=user_id))
        
        
def send_otp(user, otp):
    subject = 'OTP: Confirm email'
    msg = f'Dear {user.fname}\n'
    msg += f'Please use the code below to confirm your email address.\n'
    msg += f'OTP: {otp.code}\n'
    msg += f'\n'
    msg += f'This code will expire in 10 minutes.\n\n'
    msg += f'Kind regards,\nWastewise'
    
    return send_email(user.email, subject, msg)
    
   

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
    
    
def validatePassword(password1, password2):
    
    if password1 != password2:
        return False
    else:
        return True
    
    
    
def checkProfile(user_id):
    
    user = User.query.get(user_id)
    if Participant.query.filter_by(user_id = user.id).first():
        return True
    else:
        return False
    
def getParticipant(user_id):
    user = User.query.get(user_id)
    return Participant.query.filter_by(user_id = user.id).first()
