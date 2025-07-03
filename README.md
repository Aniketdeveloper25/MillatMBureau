# Muslim Nikah Marriage Bureau

A Flask web application for Muslim matrimony services.

## Deployment Instructions for Render

### Prerequisites
- GitHub account
- Render.com account
- Firebase project with Realtime Database

### Steps to Deploy

1. **Prepare Firebase Credentials**
   - Make sure your `firebase_key.json` file is properly configured
   - Note: This file should be kept secure and not committed to public repositories

2. **Set Up Environment Variables in Render**
   - SECRET_KEY: A secure secret key for your Flask application
   - RENDER: Set to 'true' to indicate production environment
   - PORT: Set to 10000 (or your preferred port)
   
3. **Deploy to Render**
   - Connect your GitHub repository to Render
   - Create a new Web Service
   - Select the repository and branch
   - Render will automatically detect the configuration from render.yaml
   - Deploy the application

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python run.py`
4. Access the application at http://127.0.0.1:5000

## Features

- User registration and authentication
- Profile creation and management
- Match suggestions
- Admin dashboard for managing users and matches
- Responsive design for mobile and desktop

## Environment
- Python 3.8+
- Flask
- Firebase Realtime Database

## Notes
- Make sure your Firebase Realtime Database rules allow read/write for development.
- For production, secure your database rules. 