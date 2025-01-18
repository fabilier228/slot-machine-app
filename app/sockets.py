from flask import Blueprint, jsonify, Response
from .models import User
import json
import random
import time
from . import socketio
from flask_socketio import emit, send
from threading import Thread

def get_advertisement_from_json():
    with open('adverts.json', 'r', encoding='utf-8') as f:
        ads = json.load(f)
        ad = random.choice(ads)
        return ad['description']

def generate_advertisements():
    while True:
        ad = get_advertisement_from_json()
        yield f"data: {ad}\n\n"
        time.sleep(5)

@socketio.on('connect')
def connect_user():
    print("connected")

@socketio.on('event')
def send_random_user_win():
    users = User.query.all()
    winner = random.choice(users)
    amount_win = random.randint(1,5000)
    message = f"🎉 {winner.username} just won {amount_win}$ ! 🎉"
    emit('new_winner', {'message': message})

sockets = Blueprint('sockets', __name__)


@sockets.route('/events/datetime')
def stream():
    return Response(generate_advertisements(), content_type='text/event-stream')
