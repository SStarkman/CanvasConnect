from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required, current_user
#from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Check if user is authenticated before showing the dashboard"""
    if "credentials" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html")  # Show the dashboard11

@main.route('/new')
def new_group():
    return render_template("new_group.html")

