import firebase_admin
from firebase_admin import credentials
import json
import requests
import os

def update_database_rules():
    print("Updating database rules...")
    
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
    
    # Read the rules file
    with open('database.rules.json', 'r') as f:
        rules = json.load(f)
    
    # Update the database rules
    print(f"Updating rules for database {project_id}-default-rtdb...")
    rules_url = f"https://firebase.googleapis.com/v1beta1/projects/{project_id}/locations/us-central1/instances/{project_id}-default-rtdb"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Get current database info
    get_response = requests.get(rules_url, headers=headers)
    if get_response.status_code != 200:
        print(f"Error getting database info: {get_response.text}")
        return False
    
    db_info = get_response.json()
    
    # Update with new rules
    db_info['databaseUrl'] = f"https://{project_id}-default-rtdb.firebaseio.com"
    db_info['type'] = "USER_DATABASE"
    db_info['state'] = "ACTIVE"
    
    # Add rules to the request
    db_info['securityRules'] = {
        "rules": rules["rules"]
    }
    
    # Send the update request
    update_response = requests.patch(
        rules_url, 
        headers=headers, 
        json=db_info
    )
    
    if update_response.status_code == 200:
        print("Database rules updated successfully!")
        return True
    else:
        print(f"Error updating database rules: {update_response.text}")
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

if __name__ == "__main__":
    success = update_database_rules()
    
    if success:
        print("Database rules update successful!")
        exit(0)
    else:
        print("Database rules update failed!")
        exit(1) 