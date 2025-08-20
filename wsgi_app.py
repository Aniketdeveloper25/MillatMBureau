from app import create_app
from flask import jsonify

# Create the Flask application
app = create_app()

# Add a test route
@app.route('/api/test')
def test_route():
    return jsonify({"status": "ok", "message": "Application is running correctly"})

# This is the object that Gunicorn will use
application = app

if __name__ == "__main__":
    app.run() 