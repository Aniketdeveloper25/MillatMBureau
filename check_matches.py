import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase
cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://muslim-nikah-d4ea4-default-rtdb.firebaseio.com/'
})

# Get users and matches
users = db.reference('users').get() or {}
matches = db.reference('matches').get() or {}

print('\nUsers:', len(users))
for uid, user in users.items():
    print(f"\nUser: {user.get('fullname')}")
    print(f"Gender: {user.get('gender')}")
    print(f"Age: {user.get('age')}")
    print(f"Location: {user.get('location')}")
    print(f"Preferences: {user.get('preferences')}")

print('\nMatches:', len(matches))
for mid, match in matches.items():
    user1 = users.get(match.get('user1_id', ''), {})
    user2 = users.get(match.get('user2_id', ''), {})
    print(f"\nMatch ID: {mid}")
    print(f"User 1: {user1.get('fullname')} ({user1.get('gender')}, {user1.get('age')})")
    print(f"User 2: {user2.get('fullname')} ({user2.get('gender')}, {user2.get('age')})")
    print(f"Score: {match.get('match_score')}")
    print(f"Status: {match.get('status')}")