from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user
from sqlalchemy import desc
from paramiko.client import SSHClient
from datetime import datetime, timedelta
from .models import GameLog, User
from . import db
import paramiko
import json
import time
import random


def get_who_from_server():
    HOSTNAME = "sigma.ug.edu.pl"
    PORT = 22
    USER = "jkunikowski"
    COMMAND = "who | wc -l"
    PRIVATE_KEY_PATH = "../.ssh/id_rsa_sigma"

    try:
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        with open(PRIVATE_KEY_PATH, "r") as key:
            private_key = paramiko.RSAKey.from_private_key(key)

        client.connect(HOSTNAME, port=PORT, username=USER, pkey=private_key)

        stdin, stdout, stderr = client.exec_command(COMMAND)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            return int(output)
        elif error:
            print(f"Error: {error}")
        else:
            print("No output, file may not exist or is empty.")

    except Exception as err:
        print(err)


views = Blueprint('views', __name__)


bonus_collection_times = {}


@views.route('/main', methods=["GET", "POST"])
@login_required
def main():
    saldo = current_user.saldo
    current_online = get_who_from_server()
    return render_template("main.html", user=current_user, saldo=saldo, online_people=current_online)


@views.route('/')
def home():
    return render_template("home.html")


@views.route('/profile')
@login_required
def profile_page():
    saldo = current_user.saldo
    current_online = get_who_from_server()

    user_history = GameLog.query.filter_by(user_id=current_user.id).order_by(desc(GameLog.timestamp)).limit(20).all()

    return render_template('profile.html', game_history=user_history, saldo=saldo, online_people=current_online)

@views.route('/ranking')
@login_required
def ranking_page():
    saldo = current_user.saldo
    current_online = get_who_from_server()

    search_query = request.args.get('search', '')

    if search_query:
        best_wins = GameLog.query.join(User).filter(
            User.username.like(f"%{search_query}%")
        ).order_by(desc(GameLog.result)).limit(25).all()
    else:
        best_wins = GameLog.query.order_by(desc(GameLog.result)).limit(25).all()

    user_ids = [win.user_id for win in best_wins]
    users = {user.id: user.username for user in User.query.filter(User.id.in_(user_ids)).all()}

    return render_template('ranking.html', biggest_wins=best_wins, saldo=saldo, online_people=current_online,
                           users=users, search=search_query)


@views.route('/update_saldo', methods=["POST"])
@login_required
def update_saldo():
    data = request.get_json()
    winnings = data.get('winnings', 0)
    if winnings:
        current_user.saldo += winnings
        game_log = GameLog(user_id=current_user.id, result=winnings, timestamp=datetime.now())
        db.session.add(game_log)
        db.session.commit()

    else:

        game_log = GameLog(user_id=current_user.id, result=0, timestamp=datetime.now())
        db.session.add(game_log)
        db.session.commit()

    return jsonify({
        "success": True,
        "new_saldo": current_user.saldo
    })


@views.route('/collect_bonus', methods=['POST'])
@login_required
def collect_bonus():
    now = datetime.now()

    if current_user.last_bonus_collected and now - current_user.last_bonus_collected < timedelta(hours=12):
        remaining_time = current_user.last_bonus_collected + timedelta(hours=12) - now
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return jsonify(success=False, message=f"Bonus available in {hours} hours and {minutes} minutes.")

    current_user.last_bonus_collected = now
    current_user.saldo += 300
    db.session.commit()

    return jsonify(success=True, new_saldo=current_user.saldo)



@views.route('/play_game', methods=["POST"])
@login_required
def play_game():
    data = request.get_json()
    cost = data.get("cost")
    if current_user.saldo >= cost:
        current_user.saldo -= cost
        db.session.commit()
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Insufficient balance"}), 400


@views.route('/bonus_status', methods=['GET'])
@login_required
def bonus_status():
    return jsonify(
        success=True,
        last_bonus_collected=current_user.last_bonus_collected
    )

@views.route('/delete_history', methods=["DELETE"])
@login_required
def delete_history():
    try:
        user_id = current_user.id
        GameLog.query.filter_by(user_id=user_id).delete()

        db.session.commit()

        return jsonify({"message": "History deleted successfully."}), 200
    except Exception as e:
        print(f"Error deleting history: {e}")

        return jsonify({"error": "Failed to delete history."}), 500


@views.route('/update_username', methods=["UPDATE"])
@login_required
def update_username():
    data = request.get_json()
    username = data.get("newUsername")

    if not username:
        print("nie ma nazwy")
        return jsonify({"error": "Username required"}), 400

    user = User.query.get(current_user.id)
    user.username = username
    print(user.username)

    db.session.commit()
    return jsonify({"success": "Username Updated"}), 200






