from main import create_app
from waitress import serve

app = create_app()
if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=5000)