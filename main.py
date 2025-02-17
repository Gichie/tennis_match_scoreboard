from waitress import serve
from src.app import create_app


if __name__ == "__main__":
    app = create_app()
    print("Starting Waitress WSGI server on http://127.0.0.1:8080")
    serve(app.wsgi_app, host="127.0.0.1", port=8080)
