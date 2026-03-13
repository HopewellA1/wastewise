from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user


    
    
participant = Blueprint("/participant", __name__, url_prefix="/participant")

@participant.route('/new')
@login_required
def addePart():
    
    
    pass