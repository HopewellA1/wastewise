from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db  = SQLAlchemy()
bcrypt= Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecrekjhgghjklkjhghjhseonkekenhfvbdkexdntkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    
    db.init_app(app)
    # bcrypt.init_app(app)
    # login_manager.init_app(app)
    
    
    #Blueprints
    from .routes.default import default
    from .routes.auth import auth
    
    app.register_blueprint(auth)
    app.register_blueprint(default)
    
    
    with app.app_context():
        db.create_all()
    
    return app