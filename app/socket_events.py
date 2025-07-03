from app import socketio
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from flask import request

@socketio.on('connect')
def handle_connect():
    """Handle client connection to Socket.IO server"""
    if current_user.is_authenticated:
        print(f"User {current_user.id} connected to Socket.IO")
        # Join a personal room for the user
        join_room(current_user.id)
        emit('status', {'message': 'Connected to server'})
    else:
        print(f"Anonymous user connected to Socket.IO")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection from Socket.IO server"""
    if current_user.is_authenticated:
        print(f"User {current_user.id} disconnected from Socket.IO")
        # Leave the personal room
        leave_room(current_user.id)

@socketio.on('join')
def handle_join(data):
    """Handle client joining a room"""
    room = data.get('room')
    if room:
        join_room(room)
        print(f"User {current_user.id if current_user.is_authenticated else 'Anonymous'} joined room {room}")
        emit('status', {'message': f'Joined room {room}'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    """Handle client leaving a room"""
    room = data.get('room')
    if room:
        leave_room(room)
        print(f"User {current_user.id if current_user.is_authenticated else 'Anonymous'} left room {room}")
        emit('status', {'message': f'Left room {room}'}, room=room)

@socketio.on('message')
def handle_message(data):
    """Handle messages sent by clients"""
    room = data.get('room')
    message = data.get('message')
    
    if room and message:
        print(f"Message from {current_user.id if current_user.is_authenticated else 'Anonymous'} to room {room}: {message}")
        emit('message', {
            'user': current_user.id if current_user.is_authenticated else 'Anonymous',
            'message': message
        }, room=room) 