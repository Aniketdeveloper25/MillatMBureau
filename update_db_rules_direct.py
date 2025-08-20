import firebase_admin
from firebase_admin import credentials, db
import json
import os
import sys

def update_database_rules():
    """Update Firebase database rules directly."""
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
        
        # Load database rules from file
        with open('database.rules.json', 'r') as f:
            rules = json.load(f)
            
        print(f"Loaded database rules: {json.dumps(rules, indent=2)}")
        
        # Update database rules
        db_ref = db.reference('/')
        db_ref.set_rules(rules["rules"])
        print("Database rules updated successfully")
        
        # Test database connection
        test_ref = db.reference('/test')
        test_ref.set({"updated_at": firebase_admin.db.ServerValue.TIMESTAMP})
        print("Database connection test successful")
        
        # Test reviews access
        reviews_ref = db.reference('/reviews')
        test_review = {
            "test_review": {
                "user_name": "Test User",
                "rating": 5,
                "comment": "Test Comment",
                "date": "2023-01-01 00:00:00"
            }
        }
        reviews_ref.update(test_review)
        print("Reviews access test successful")
        
        # Clean up test review
        test_review_ref = db.reference('/reviews/test_review')
        test_review_ref.delete()
        print("Test review cleaned up successfully")
        
        return True
    except Exception as e:
        print(f"Error updating database rules: {e}")
        return False

if __name__ == "__main__":
    success = update_database_rules()
    if success:
        print("Database rules updated successfully")
        sys.exit(0)
    else:
        print("Failed to update database rules")
        sys.exit(1) 