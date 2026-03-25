from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from main.models.participant import Category, Contribution, Participant
from main.models.auth import User
from main import db




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
    db.session.delete(category)
    db.session.commit()
    flash("Categry delted!", "danger")
    return redirect(url_for('/admin.Categories'))


@admin.route('/submitions/<filter>', methods=['GET', 'POST'])
def submitions(filter):
    
    if filter== 'all':
        contributions = Contribution.query.all()
    else:
        contributions = Contribution.query.filter(status=filter).all()
        
    subs = list()
    
    for contri_ in contributions:
        
        user = User.query.get(Participant.query.get(contri_.Participant_Id).user_id)
        wastType = Category.query.get(contri_.Category_id)
        subs.append(
            {
                'contri_': contri_,
                "user": user,
                "username": user.first_name +'_'+ user.last_name[0],
                "categ": wastType
            }
            
        )  
        
    return render_template('admin/submitions.html', subs=subs) 
        
    
        
        