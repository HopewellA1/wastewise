from flask import Blueprint, render_template
from flask_mail import Message
from main import mail


import smtplib
from email.mime.text import MIMEText



default = Blueprint("default", __name__)

@default.route("/")
def home():
    
    
    # Gmail credentials
    sender_email = "hopewellsitshaka@gmail.com"
    receiver_email = "hopewellsitshaka@gmail.com"
    app_password = "fvugjdhinugqhrna"
    # Create the email
    subject = "Welcome"
    body = "Your account has been created."


    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    # Connect to Gmail SMTP and send email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # enable TLS
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)
    return render_template("default/home.html")

@default.route("/about")
def about():
    return render_template('default/about.html')

@default.route("/contuctUs")
def contuctUs():
    
    return render_template("default/contuctUs.html")    