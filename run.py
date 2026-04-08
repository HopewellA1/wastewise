import sys
from main import create_app, db
from waitress import serve
from main.routes.auth import createsuperuser
from main.routes.default import home
from flask_migrate import Migrate
import os



app = create_app()
migrate = Migrate(app, db)
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
#File uploading
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        with app.app_context():
            if  sys.argv[1] == 'createsuperuser':
                createsuperuser()
    else: 
               
        serve(app, host="127.0.0.1", port=5000)
        
    