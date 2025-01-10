from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/content')
@login_required
def main():
    return render_template("main.html", user=current_user)

@views.route('/')
def home():
    return render_template("home.html")
