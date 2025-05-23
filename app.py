import os
import ssl
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    my_app = Flask(__name__)

    my_app.secret_key = os.getenv("FLASK_APP_SECRET_KEY")
    my_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_CONNECTOR")
    db.init_app(my_app)

    # Register the auth blueprint
    from routes.auth import auth # import the auth blueprint
    my_app.register_blueprint(auth, url_prefix="/auth")  # make sure the URL prefix is "/auth"

    # blueprint for non-auth parts of app
    from routes.main import main
    my_app.register_blueprint(main)


    return my_app

# One-time creation
app = create_app()
with app.app_context():
    db.create_all() # Create Tables for the database
    print("Tables created")

if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    app.run(ssl_context=context, host="0.0.0.0", port=8080)