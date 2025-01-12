from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc
from paramiko.client import SSHClient
from datetime import datetime, timedelta
from . import db
from .models import GameLog
import paramiko


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
def profile_page():
    saldo = current_user.saldo
    current_online = get_who_from_server()

    user_history = GameLog.query.filter_by(user_id=current_user.id).order_by(desc(GameLog.timestamp)).limit(20).all()

    return render_template('profile.html', game_history=user_history, saldo=saldo, online_people=current_online)


@views.route('/update_saldo', methods=["POST"])
@login_required
def update_saldo():
    data = request.get_json()
    winnings = data.get('winnings', 0)
    if winnings:
        print("wchodzi w baze")
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
    user_id = current_user.id
    now = datetime.now()

    last_collected = bonus_collection_times.get(user_id)
    if last_collected and now - last_collected < timedelta(hours=12):
        remaining_time = last_collected + timedelta(hours=12) - now
        return jsonify(success=False, message=f"Bonus available in {remaining_time}.")

    bonus_collection_times[user_id] = now
    current_user.saldo += 300
    print(current_user.saldo)
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
