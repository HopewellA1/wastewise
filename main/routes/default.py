from flask import Blueprint, render_template

default = Blueprint("default", __name__)

@default.route("/")
def home():
    return render_template("default/home.html")

@default.route("/about")
def about():
    return render_template('default/about.html')

@default.route("/contuctUs")
def contuctUs():
    
    return render_template("default/contuctUs.html")    