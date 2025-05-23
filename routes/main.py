from datetime import datetime, timezone
import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from routes.models import Group, User, Membership

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Check if user is authenticated before showing the dashboard"""
    if "credentials" not in session:
        return redirect(url_for("auth.login"))

    # Get all groups and take out ones that the person is busy during those times
    groups = Group.query.all() # Gets all groups
    return render_template("dashboard.html", groups = groups)  # Show the dashboard11

@main.route('/new-group', methods=['GET'])
def new_group():
    return render_template("new_group.html")

# Added for submission
@main.route('/submit-group', methods=['POST'])
def submit_group():
    # This handles the form submission
    group_title = request.form['group-title']
    group_description = request.form['group-description']
    tag = request.form['tag']
    start_date_time = datetime.strptime(request.form['start-date-time'], '%Y-%m-%dT%H:%M')
    end_date_time = datetime.strptime(request.form['end-date-time'], '%Y-%m-%dT%H:%M')

    user = get_user()

    if user:
        if(is_busy(start_date_time, end_date_time)):
            flash("You are busy at that time.", "warning")
            return redirect(url_for('main.index'))  # Redirect to a page that lists the group

        # Create and add to the database
        group = Group(
            title=group_title,
            description=group_description,
            tag=tag,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            organizer_id= user.id
        )

        db.session.add(group)
        db.session.commit()

        add_to_calendar(group.id)

        return redirect(url_for('main.index'))  # Redirect to a page that lists the groups

    else:
        return "User not found", 404

@main.route('/join-group', methods=['POST'])
def join_group():
    group_id = request.form.get('group_id')
    user = get_user()

    new_membership = Membership(
        user_id = user.id,
        group_id = group_id
    )

    db.session.add(new_membership)
    db.session.commit()

    add_to_calendar(group_id)

    return redirect(url_for('main.index'))  # Redirect to a page that lists the groups

def add_user(user_email, user_name):
    print(f"{user_email} not in user table. Adding user now.")
    new_user = User(
        name=user_name,
        email=user_email
    )
    db.session.add(new_user)
    db.session.commit()

def get_user():
    user_email = session.get('user_email')
    user_name = session.get('user_name')
    if user_email:
        print("User-email", user_email)
        user = User.query.filter(User.email==user_email).first()
        print("User", user)
        if not user:
            add_user(user_email, user_name)

        user = User.query.filter(User.email==user_email).first()
        return user
    else:
        return redirect(url_for('auth.login'))

def add_to_calendar(group_id):
    # The endpoint to create a new event in the primary calendar
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    # Access token from session (assumes you've already authenticated and stored this)
    access_token = session['credentials']['token']

    group = Group.query.get(group_id)
    event = {
        'summary': group.title,
        'description': group.description,
        'start': {
            'dateTime': group.start_date_time.isoformat(),
            'timeZone': 'UTC'
        },
        'end': {
            'dateTime': group.end_date_time.isoformat(),
            'timeZone': 'UTC'
        }
    }


    headers={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=event)


    if response.status_code == 200 or response.status_code == 201:
        print('Event created:', response.json()['htmlLink'])
    else:
        print('Failed to create event:', response.text)

def is_busy(start, end):
    # The endpoint to create a new event in the primary calendar
    url = "https://www.googleapis.com/calendar/v3/freeBusy"

    # Access token from session (assumes you've already authenticated and stored this)
    access_token = session['credentials']['token']

    headers={
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    event = {
        "timeMin": start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "timeMax": end.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "timeZone": "UTC",
        "items": [
            {"id": "primary"}
        ]
    }
    # Make the POST request
    response = requests.post(url, headers=headers, json=event)

    if response.status_code == 200 or response.status_code == 201:
        return response.json()["calendars"]["primary"]["busy"]
    else:
        print('Failed', response.text)

