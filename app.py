from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
import os
import time

app = Flask(__name__)
import secrets
app.config['SECRET_KEY'] = secrets.token_hex(32)
socketio = SocketIO(app, cors_allowed_origins="*")

# File to store the content
CONTENT_FILE = 'shared_content.txt'

# Configuration limits
MAX_TEXT_SIZE = 10000000  # 10MB - adjust as needed
MAX_CONNECTIONS = 50    # Max simultaneous users

# Track online users
online_users = set()
user_stats = {'total_chars': 0, 'total_words': 0, 'total_lines': 0}

def read_content():
    if os.path.exists(CONTENT_FILE):
        with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def save_content(content):
    # Enforce size limit
    if len(content) > MAX_TEXT_SIZE:
        content = content[:MAX_TEXT_SIZE]
    
    with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    update_stats(content)
    return len(content)

def update_stats(content):
    user_stats['total_chars'] = len(content)
    user_stats['total_words'] = len(content.split()) if content.strip() else 0
    user_stats['total_lines'] = content.count('\n') + 1 if content else 0

@app.route('/')
def index():
    content = read_content()
    update_stats(content)
    return render_template('index.html', content=content)

@socketio.on('connect')
def handle_connect():
    if len(online_users) >= MAX_CONNECTIONS:
        disconnect()
        return False
    
    online_users.add(request.sid)
    emit('user_count', {'count': len(online_users)}, broadcast=True)
    emit('stats_update', user_stats)
    emit('limits', {'max_size': MAX_TEXT_SIZE})

@socketio.on('disconnect')
def handle_disconnect():
    online_users.discard(request.sid)
    emit('user_count', {'count': len(online_users)}, broadcast=True)

@socketio.on('text_change')
def handle_text_change(data):
    content = data.get('content', '')
    saved_length = save_content(content)
    
    # If content was truncated, notify client
    if len(content) > MAX_TEXT_SIZE:
        emit('content_truncated', {'max_size': MAX_TEXT_SIZE})
        content = content[:MAX_TEXT_SIZE]
    
    emit('content_updated', {'content': content}, broadcast=True, include_self=False)
    emit('stats_update', user_stats, broadcast=True)

@socketio.on('cursor_position')
def handle_cursor_position(data):
    emit('cursor_update', {'user': request.sid, 'position': data['position']}, broadcast=True, include_self=False)

if __name__ == '__main__':
    print(f"Server starting...")
    print(f"Access the editor at: http://localhost:5000")
    print(f"Content will be saved to: {os.path.abspath(CONTENT_FILE)}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)