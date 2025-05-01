from datetime import datetime

from flask import Blueprint, render_template, session, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from routes.models import Group, User, Membership

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Check if user is authenticated before showing the dashboard"""
    if "credentials" not in session:
        return redirect(url_for("auth.login"))

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

        return redirect(url_for('main.index'))  # Redirect to a page that lists the groups

    else:
        return "User not found", 404

@main.route('/join-group', methods=['POST'])
def join_group():
    print("Join Group Clicked")
    group_id = request.form.get('group_id')
    user = get_user()
    print("Group id", group_id, "user", user)
    new_membership = Membership(
        user_id = user.id,
        group_id = group_id
    )

    print("new membership created")

    db.session.add(new_membership)
    db.session.commit()

    print("Added to database")

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