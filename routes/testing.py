import os
import json
import ssl

from flask import Flask, redirect, url_for, session, request, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_APP_SECRET_KEY")  # Change this to a secure value

# Load OAuth credentials from JSON file
GOOGLE_CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRETS_FILE")
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Create OAuth flow
flow = Flow.from_client_secrets_file(
    GOOGLE_CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri="https://localhost:5000/callback"
)

@app.route("/")
def home():
    return '<a href="/login">Login with Google</a>'

@app.route("/login")
def login():
    """Redirect user to Google's OAuth login page"""
    auth_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """Handle OAuth callback and store user credentials"""
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # Save credentials in session
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    """Display user's calendar events"""
    if "credentials" not in session:
        return redirect(url_for("login"))

    creds = Credentials(**session["credentials"])
    service = build("calendar", "v3", credentials=creds)

    # Fetch next 5 calendar events
    events_result = service.events().list(
        calendarId="primary",
        maxResults=5,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    return jsonify(events)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    # Create an SSL context and load your certificate and key
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    # Run the app with SSL (HTTPS) and the context
    app.run(ssl_context=context, host="0.0.0.0", port=5000)
    # Make sure the port is set to 5000
   # app.run(ssl_context=context, host="0.0.0.0", port=5000)
    #app.run(ssl_context=('cert.pem', 'key.pem'))
    # Run Flask app with SSL context
   # app.run(ssl_context = 'adhoc')
