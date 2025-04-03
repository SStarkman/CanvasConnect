import os
import ssl

from flask import Flask
from routes.main import main
from routes.auth import auth

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_APP_SECRET_KEY")  # Change this to a secure value

# Register Blueprints
app.register_blueprint(main)
app.register_blueprint(auth, url_prefix="/auth")

if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    app.run(ssl_context=context, host="0.0.0.0", port=5000)