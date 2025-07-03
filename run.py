from app import create_app, socketio
import sys
import socket
import os

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except OSError:
            return True

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Check if running in production (Render) or development
    if os.environ.get('RENDER'):
        # In production, use the PORT environment variable
        port = int(os.environ.get("PORT", 10000))
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    else:
        # In development, use port detection
        port_options = [5000, 5001]
        available_port = None
        
        for port in port_options:
            if not is_port_in_use(port):
                available_port = port
                break
        
        if available_port:
            print(f"Starting server on port {available_port}")
            socketio.run(app, host='127.0.0.1', port=available_port, debug=True)
        else:
            print("Error: No available ports found. Please free up one of these ports:", port_options)
            sys.exit(1) 