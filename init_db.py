import firebase_admin
from firebase_admin import credentials, db
import sys
import time
import requests
import json

def create_firebase_database():
    # Load the service account key
    with open('firebase_key.json', 'r') as f:
        service_account = json.load(f)
    
    # Extract project ID
    project_id = service_account['project_id']
    
    # Get access token
    print("Getting access token...")
    auth_url = f"https://oauth2.googleapis.com/token"
    auth_data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": create_jwt(service_account)
    }
    
    auth_response = requests.post(auth_url, data=auth_data)
    if auth_response.status_code != 200:
        print(f"Error getting access token: {auth_response.text}")
        return False
    
    access_token = auth_response.json().get('access_token')
    
    # Create the Realtime Database
    print(f"Creating Realtime Database for project {project_id}...")
    db_url = f"https://firebasedatabase.googleapis.com/v1beta/projects/{project_id}/locations/us-central1/instances?databaseId={project_id}-default-rtdb"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    db_response = requests.post(db_url, headers=headers, json={})
    
    if db_response.status_code == 200 or db_response.status_code == 201:
        print("Database created successfully!")
        return True
    elif db_response.status_code == 409:
        print("Database already exists!")
        return True
    else:
        print(f"Error creating database: {db_response.text}")
        return False

def create_jwt(service_account):
    import jwt
    import datetime
    
    # Get the private key from the service account
    private_key = service_account['private_key']
    client_email = service_account['client_email']
    
    # Create JWT payload
    now = datetime.datetime.utcnow()
    payload = {
        'iss': client_email,
        'sub': client_email,
        'aud': 'https://oauth2.googleapis.com/token',
        'iat': now,
        'exp': now + datetime.timedelta(minutes=60),
        'scope': 'https://www.googleapis.com/auth/firebase.database https://www.googleapis.com/auth/cloud-platform'
    }
    
    # Sign the JWT
    signed_jwt = jwt.encode(payload, private_key, algorithm='RS256')
    return signed_jwt

def initialize_database():
    # First, try to create the database if it doesn't exist
    try:
        create_firebase_database()
    except Exception as e:
        print(f"Error creating database: {e}")
        # Continue anyway, as the database might already exist
    
    # Check if Firebase app is already initialized
    try:
        default_app = firebase_admin.get_app()
    except ValueError:
        # Initialize Firebase app if not already initialized
        cred = credentials.Certificate('firebase_key.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://muslim-nikah-d4ea4-default-rtdb.firebaseio.com/'
        })
    
    print("Initializing database structure...")
    
    # Create the basic database structure
    try:
        # Check if users node exists
        users_ref = db.reference('users')
        users_data = users_ref.get()
        
        # Check if matches node exists
        matches_ref = db.reference('matches')
        matches_data = matches_ref.get()
        
        if matches_data is None:
            print("Creating matches node...")
            matches_ref.set({})
        
        if users_data is None:
            print("Creating 'users' node...")
            db.reference('users').set({})
        else:
            print("'users' node already exists")
        
        # Check if conversations node exists
        conversations_ref = db.reference('conversations')
        conversations_data = conversations_ref.get()
        
        if conversations_data is None:
            print("Creating 'conversations' node...")
            db.reference('conversations').set({})
        else:
            print("'conversations' node already exists")
        
        # Check if messages node exists
        messages_ref = db.reference('messages')
        messages_data = messages_ref.get()
        
        if messages_data is None:
            print("Creating 'messages' node...")
            db.reference('messages').set({})
        else:
            print("'messages' node already exists")
        
        # Check if career_opportunities node exists
        careers_ref = db.reference('career_opportunities')
        careers_data = careers_ref.get()
        
        if careers_data is None:
            print("Creating 'career_opportunities' node...")
            db.reference('career_opportunities').set({})
        else:
            print("'career_opportunities' node already exists")
        
        # Check if job_applications node exists
        applications_ref = db.reference('job_applications')
        applications_data = applications_ref.get()
        
        if applications_data is None:
            print("Creating 'job_applications' node...")
            db.reference('job_applications').set({})
        else:
            print("'job_applications' node already exists")
        
        # Check if chat_messages node exists
        chat_ref = db.reference('chat_messages')
        chat_data = chat_ref.get()
        
        if chat_data is None:
            print("Creating 'chat_messages' node...")
            db.reference('chat_messages').set({})
        else:
            print("'chat_messages' node already exists")
        
        print("Database structure initialization complete!")
        return True
    except Exception as e:
        print(f"Error initializing database structure: {e}")
        return False

if __name__ == "__main__":
    success = initialize_database()
    
    if success:
        print("Database initialization successful!")
        sys.exit(0)
    else:
        print("Database initialization failed!")
        sys.exit(1)