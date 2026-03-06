from flask import render_template, Blueprint

auth = Blueprint("/auth", __name__, url_prefix="/auth")

@auth.route("/signup")
def signup():
    
    return render_template("auth/signup.html")