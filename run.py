import sys
from main import create_app
from waitress import serve
from main.routes.auth import createsuperuser
from main.routes.default import home


app = create_app()

    

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        with app.app_context():
            if  sys.argv[1] == 'createsuperuser':
                createsuperuser()
    else: 
               
        serve(app, host="127.0.0.1", port=5000)
        
    