from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import os
from utils.encryption import encrypt_message, decrypt_message
from utils.auth import require_login

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app)

# In-memory storage for demo purposes
users = {}
messages = []
rooms = ['General']

@app.route('/')
@require_login
def index():
    return render_template('index.html', rooms=rooms, username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return 'User already exists'
        users[username] = {'password': generate_password_hash(password)}
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/search_messages', methods=['POST'])
def search_messages():
    query = request.json.get('query', '').lower()
    results = [msg for msg in messages if query in msg['message'].lower()]
    return jsonify(results)

@app.route('/profile', methods=['GET', 'POST'])
@require_login
def profile():
    if request.method == 'POST':
        # Handle profile update (e.g., picture upload)
        pass
    return render_template('profile.html', username=session['username'])

@socketio.on('send_message')
def handle_message(data):
    username = session.get('username')
    message = encrypt_message(data['message'])
    room = data['room']
    messages.append({'username': username, 'message': message, 'room': room})
    emit('receive_message', {'username': username, 'message': decrypt_message(message)}, room=room)

@socketio.on('join')
def handle_join(data):
    username = session.get('username')
    room = data['room']
    join_room(room)
    emit('user_joined', {'username': username}, room=room)

@socketio.on('leave')
def handle_leave(data):
    username = session.get('username')
    room = data['room']
    leave_room(room)
    emit('user_left', {'username': username}, room=room)

@socketio.on('user_status')
def handle_user_status(data):
    username = data['username']
    status = data['status']
    emit('update_user_status', {'username': username, 'status': status}, broadcast=True)

@socketio.on('react_message')
def handle_react_message(data):
    message_id = data['messageId']
    reaction = data['reaction']
    emit('update_reaction', {'messageId': message_id, 'reaction': reaction}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
