from flask import Blueprint, request, jsonify, render_template
from .models import User, GameLog
from . import db

main = Blueprint('main', __name__)

@main.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(username=data['username'], password=data['password'])  # Hasło powinno być zaszyfrowane
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

@main.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'id': user.id, 'username': user.username})

@main.route('/games', methods=['POST'])
def log_game():
    data = request.json
    new_log = GameLog(user_id=data['user_id'], result=data['result'])
    db.session.add(new_log)
    db.session.commit()
    return jsonify({'message': 'Game log created'}), 201

# Dodaj endpointy do UPDATE, DELETE i wyszukiwania
@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')
