from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
from flask_mail import Mail
from dotenv import load_dotenv



load_dotenv()

db  = SQLAlchemy()
bcrypt= Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
mail = Mail()

@login_manager.user_loader
def load_user(id):
    from .models.auth import User
    return User.query.get(int(id))


def create_app():
    app = Flask(__name__)
    csrf = CSRFProtect()
    app.config['SECRET_KEY'] = 'supersecrekjhgghjklkjhghjhseonkekenhfvbdkexdntkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    
    #Flask Extensions
    db.init_app(app)
    csrf.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    
    
    #Blueprints
    from .routes.default import default
    from .routes.auth import auth
    
    app.register_blueprint(auth)
    app.register_blueprint(default)
    
    
    
    #Email config  
    from flask_mail import Mail

    # app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    # app.config['MAIL_PORT'] = 465
    # app.config['MAIL_USE_TLS'] = False
    # app.config['MAIL_USE_SSL'] = True
    # app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")
    # app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASS")
    # app.config['MAIL_DEFAULT_SENDER'] = os.getenv("EMAIL_USER")
    
    
    
    with app.app_context():
        from .models.auth import User
        db.create_all()
    
    return app