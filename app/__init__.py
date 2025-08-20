import os
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_login import LoginManager, current_user
import firebase_admin
from firebase_admin import credentials, db
import datetime
from flask_socketio import SocketIO
import json
import sys
import uuid
from .translations import get_translation

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
            # Try both firebase_key.json and firebase_key2.json
            try:
                cred = credentials.Certificate("firebase_key.json")
                print("Successfully loaded firebase_key.json")
            except Exception as e:
                print(f"Failed to load firebase_key.json: {e}")
                try:
                    cred = credentials.Certificate("firebase_key2.json")
                    print("Successfully loaded firebase_key2.json")
                except Exception as e:
                    print(f"Failed to load firebase_key2.json: {e}")
                    raise Exception("No valid Firebase credentials found")
        
        # Initialize Firebase app if not already initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://muslim-nikah-d4ea4-default-rtdb.firebaseio.com/'
            })
            print("Firebase app initialized successfully")
        else:
            print("Firebase app already initialized")
            
        # Get database reference
        database = db.reference()
        
        # Test database connection
        try:
            test = database.child('test').get()
            print("Database connection test successful")
        except Exception as e:
            print(f"Database connection test failed: {e}")
            
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
    
    # Add translation function to Jinja2 environment
    @app.context_processor
    def inject_globals():
        return {
            'now': datetime.datetime.now(),
            '_': lambda text: get_translation(text, 'en')  # Always use English
        }
    
    # Home route - accessible without login
    @app.route('/')
    def index():
        # Get all reviews to display on homepage
        if database:
            try:
                reviews_ref = database.child('reviews').get()
                reviews = reviews_ref if reviews_ref else {}
                print(f"Retrieved {len(reviews) if reviews else 0} reviews for homepage")
            except Exception as e:
                print(f"Error getting reviews: {e}", file=sys.stderr)
                reviews = {}
        else:
            print("Database not initialized, showing empty reviews")
            reviews = {}
        return render_template('index.html', reviews=reviews)
    
    # About Us page - accessible without login
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    # Careers functionality removed
    
    # Health check endpoint for monitoring
    @app.route('/health')
    def health_check():
        return jsonify({"status": "ok"})
    
    return app