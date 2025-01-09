from app import create_app, db, socketio
from flask_socketio import emit
from random import choice

app = create_app()

@socketio.on('play_slot')
def handle_play_slot(data):
    result = choice(['Win', 'Lose', 'Draw'])
    emit('slot_result', {'result': result}, broadcast=True)

if __name__ == '__main__':
    db.create_all(app=create_app())
    socketio.run(app, debug=True)
