import os

import requests
from flask import Blueprint, Flask, redirect, url_for, session, request, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from app import db

auth = Blueprint('auth', __name__)

# Load OAuth credentials from environment variable
GOOGLE_CLIENT_SECRETS_FILE = os.getenv("GOOGLE_CLIENT_SECRETS_FILE")
SCOPES = [
          "openid",
          "https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/userinfo.profile",  # User's profile info (name, picture)
          "https://www.googleapis.com/auth/userinfo.email"  # User's email
          ]


# Create OAuth flow
flow = Flow.from_client_secrets_file(
    GOOGLE_CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri='https:/ec2-18-212-164-135.compute-1.amazonaws.com:8080/:8080/callback'
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

    # Use credentials to fetch user info
    user_info = get_user_info(credentials)

    # Now store user info in the session (name, email, etc.)
    session["user_name"] = user_info["name"]
    session["user_email"] = user_info["email"]

    return redirect(url_for("main.index"))

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


def get_user_info(credentials):
    """Fetch user info using the OAuth credentials"""

    # Set up the headers with the OAuth token
    headers = {
        "Authorization": f"Bearer {credentials.token}"
    }

    # Make a request to the Google People API for user info
    response = requests.get("https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses",
                            headers=headers)

    if response.status_code == 200:
        # Parse the JSON response from the People API
        user_info = response.json()
        return {
            "name": user_info["names"][0]["displayName"],
            "email": user_info["emailAddresses"][0]["value"]
        }
    else:
        raise Exception(f"Failed to fetch user info: {response.status_code}, {response.text}")

