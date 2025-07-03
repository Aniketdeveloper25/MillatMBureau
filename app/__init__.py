import os
from flask import Flask, render_template, jsonify
from flask_login import LoginManager
import firebase_admin
from firebase_admin import credentials, db
import datetime
from flask_socketio import SocketIO
import json
import sys

# Initialize Flask-Login
login_manager = LoginManager()

# Initialize Socket.IO
socketio = SocketIO()

# Global database reference
database = None

def create_app():
    # Initialize Firebase
    global database
    try:
        # Try to get credentials from environment variable first (for production)
        if os.environ.get('FIREBASE_CREDENTIALS'):
            print("Using Firebase credentials from environment variable")
            cred_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
            cred = credentials.Certificate(cred_dict)
        else:
            print("Using Firebase credentials from file")
            cred = credentials.Certificate("firebase_key.json")
        
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://muslim-nikah-d4ea4-default-rtdb.firebaseio.com/'
            })
        database = db.reference()
        print("Firebase initialized successfully")
    except Exception as e:
        print(f"Firebase initialization error: {e}", file=sys.stderr)
        # Create a placeholder for database if initialization fails
        database = None
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'
    
    # Initialize Socket.IO with the app
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints
    from .user import user_bp
    from .admin import admin_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Import Socket.IO event handlers
    from . import socket_events
    
    # Make datetime available to all templates
    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.datetime.now()
        }
    
    # Home route - accessible without login
    @app.route('/')
    def index():
        # Get all reviews to display on homepage
        if database:
            try:
                reviews_ref = database.child('reviews').get()
                reviews = reviews_ref if reviews_ref else {}
            except Exception as e:
                print(f"Error getting reviews: {e}", file=sys.stderr)
                reviews = {}
        else:
            reviews = {}
        return render_template('index.html', reviews=reviews)
    
    # About Us page - accessible without login
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "ok",
            "firebase_initialized": database is not None
        })
    
    return app