from flask import Blueprint, render_template
from flask_mail import Message
#from main import mail


default = Blueprint("default", __name__)

@default.route("/")
def home():
    
    # msg = Message(
    #     subject="Welcome",
    #     recipients=["hopewellsitshaka@gmail.com"],
    #     sender='hopewellsitshaka@gmail.com',
        
    # )

    # msg.body = "Your account has been created."

    # mail.send(msg)
    return render_template("default/home.html")

@default.route("/about")
def about():
    return render_template('default/about.html')

@default.route("/contuctUs")
def contuctUs():
    
    return render_template("default/contuctUs.html")    