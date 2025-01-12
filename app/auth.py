from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
import bcrypt
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user.password):
                flash("Logged in succesfully!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.main'))
            else:
                flash("Incorrect password, try again.", category='error')
        else:
            flash("Username does not exist.", category='error')

    return render_template("login.html", user=current_user)

@auth.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user_email = User.query.filter_by(email=email).first()
        user_name = User.query.filter_by(username=username).first()

        if user_email or user_name:
            flash("Email or username already exists.", category='error')
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category='error')
        elif len(username) < 2:
            flash("Username must be greater than 1 characters.", category='error')
        elif password1 != password2:
            flash("Password dont\'t match.", category='error')
        elif len(password1) < 6:
            flash("Password must be at least 6 characters.", category='error')
        else:
            hashed_password = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())
            new_user = User(email=email, username=username, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            flash("Account Created", category='success')

            return redirect(url_for('views.main'))


    return render_template("signup.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))