from flask import Blueprint, render_template, url_for, request, redirect, flash, flash
from main.models.auth import User
from main import db, bcrypt
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user
from getpass import getpass

auth = Blueprint("/auth", __name__, url_prefix="/auth")

@auth.route("/signup", methods=['POST', 'GET'])
def signup():
    
   
        
    if  request.method == 'POST':
        try:
            if validatePassword(request.form['password'], request.form['password2']):
                new_user = User(
                    fname=request.form['first_name'],
                    lname=request.form['last_name'],
                    email=request.form['email'].lower(),
                    
                    password= bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
                )
                db.session.add(new_user)
                db.session.commit()
                flash(f'user({new_user.email}) account created successfully!', 'success')
                return redirect(url_for('default.home'))
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
        
        if user and bcrypt.check_password_hash(user.password, password):
            
            login_user(user)
            print("user: ", user)
        
            return redirect(url_for('default.home'))
        else:
            
            flash("Invalid login details","danger" )
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
        
        return render_template('auth/account.html', user=user)
    elif request.method == 'POST':
        
        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.email = request.form["email"]
        
        
        
        try:
            user.is_staff  = "is_staff" in request.form
            user.is_superuser = "is_superuser" in request.form
        except:
             pass
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
        
        pass
    elif request.method == 'GET':
        
        return render_template('auth/reset_password_request.html')
    

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