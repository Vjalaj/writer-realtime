from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, disconnect
import os
import time

app = Flask(__name__)
import secrets
app.config['SECRET_KEY'] = secrets.token_hex(32)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration limits
MAX_TEXT_SIZE = 10000000  # 10MB - adjust as needed
MAX_CONNECTIONS = 50    # Max simultaneous users
MAX_NOTEBOOKS = 10      # Max notebooks per session

# Notebook management
notebooks = {}
current_notebook = 'default'

def get_notebook_file(name):
    return f'notebook_{name}.txt'

def create_notebook(name):
    if len(notebooks) >= MAX_NOTEBOOKS:
        return False
    if name not in notebooks:
        notebooks[name] = {'title': name, 'created': time.time()}
        # Create empty file if doesn't exist
        filepath = get_notebook_file(name)
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('')
        return True
    return False

def get_notebook_list():
    return list(notebooks.keys())

# Initialize default notebook
create_notebook('default')

# Track online users
online_users = set()
user_stats = {'total_chars': 0, 'total_words': 0, 'total_lines': 0}

def read_content(notebook_name=None):
    if notebook_name is None:
        notebook_name = current_notebook
    filepath = get_notebook_file(notebook_name)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def save_content(content, notebook_name=None):
    if notebook_name is None:
        notebook_name = current_notebook
    # Enforce size limit
    if len(content) > MAX_TEXT_SIZE:
        content = content[:MAX_TEXT_SIZE]
    
    filepath = get_notebook_file(notebook_name)
    with open(filepath, 'w', encoding='utf-8') as f:
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
    return render_template('index.html', content=content, notebooks=get_notebook_list(), current_notebook=current_notebook)

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

@socketio.on('create_notebook')
def handle_create_notebook(data):
    name = data.get('name', '').strip()
    if name and create_notebook(name):
        emit('notebook_created', {'name': name, 'notebooks': get_notebook_list()}, broadcast=True)
    else:
        emit('notebook_error', {'message': 'Cannot create notebook. Limit reached or invalid name.'})

@socketio.on('switch_notebook')
def handle_switch_notebook(data):
    global current_notebook
    name = data.get('name')
    if name in notebooks:
        current_notebook = name
        content = read_content(name)
        update_stats(content)
        emit('notebook_switched', {'name': name, 'content': content}, broadcast=True)
        emit('stats_update', user_stats, broadcast=True)

if __name__ == '__main__':
    print(f"Server starting...")
    print(f"Access the editor at: http://localhost:5000")
    print(f"Notebooks will be saved to: {os.path.abspath('.')}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)