import os
from flask import Blueprint, Flask, redirect, url_for, session, request, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

auth = Blueprint('auth', __name__)

# Load OAuth credentials from environment variable
GOOGLE_CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRETS_FILE")
SCOPES = ["https://www.googleapis.com/auth/calendar"]


# Create OAuth flow
flow = Flow.from_client_secrets_file(
    GOOGLE_CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri="https://localhost:5000/auth/callback"
)

@auth.route("/login")
def login():
    """Redirect user to Google's OAuth login page"""
    auth_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(auth_url)


@auth.route("/callback")
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

    return redirect(url_for("main.index"))

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
