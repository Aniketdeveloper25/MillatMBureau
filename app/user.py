from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from app import login_manager, database, socketio
import firebase_admin
from firebase_admin import db, storage
import uuid
from datetime import datetime
import os
import base64
from werkzeug.utils import secure_filename
import sys

user_bp = Blueprint('user', __name__)

class User(UserMixin):
    def __init__(self, uid, data):
        self.id = uid
        self.email = data.get('email')
        self.fullname = data.get('fullname')
        self.is_admin = data.get('is_admin', False)
        self.gender = data.get('gender')
        self.age = data.get('age')
        self.location = data.get('location')
        self.phone = data.get('phone')
        self.about = data.get('about')
        self.preferences = data.get('preferences', {})
        self.profile_complete = data.get('profile_complete', False)
        # Profile picture
        self.profile_picture = data.get('profile_picture')
        # Education and job details
        self.education = data.get('education', {})
        self.job = data.get('job', {})

@login_manager.user_loader
def load_user(user_id):
    try:
        if database is None:
            print("Warning: Database is not initialized in user_loader", file=sys.stderr)
            return None
        user_data = database.child('users').child(user_id).get()
        if user_data:
            # For Realtime Database, get() returns the actual data directly
            if 'id' not in user_data:
                user_data['id'] = user_id
            return User(user_id, user_data)
    except Exception as e:
        print(f"Error in user_loader: {e}", file=sys.stderr)
    return None

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        fullname = request.form['fullname']
        password = request.form['password']
        gender = request.form['gender']
        age = request.form['age']
        location = request.form['location']

        try:
            # Get all users and filter them in Python
            all_users = database.child('users').get()
            
            # Check if email already exists
            email_exists = False
            if all_users:
                # all_users is a dictionary with user_id as keys and user_data as values
                for user_id, user_data in all_users.items():
                    if user_data and user_data.get('email') == email:
                        email_exists = True
                        break
            
            if email_exists:
                flash('Email already registered. Please use a different email.', 'danger')
                return render_template('user/register.html')

            phone = request.form['phone']

            # Get education details
            education_level = request.form.get('education_level', '')
            education_field = request.form.get('education_field', '')
            education_institute = request.form.get('education_institute', '')

            # Get job details (optional)
            job_title = request.form.get('job_title', '')
            job_company = request.form.get('job_company', '')
            job_experience = request.form.get('job_experience', '')

            # Convert job_experience to int if not empty
            if job_experience:
                try:
                    job_experience = int(job_experience)
                except ValueError:
                    job_experience = 0
            else:
                job_experience = 0

            uid = str(uuid.uuid4())
            user_data = {
                'id': uid,  # Store the ID within the user data
                'email': email,
                'fullname': fullname,
                'password': password,  # Hash in production!
                'gender': gender,
                'age': int(age),
                'location': location,
                'phone': phone,
                'about': '',
                'education': {
                    'level': education_level,
                    'field': education_field,
                    'institute': education_institute
                },
                'job': {
                    'title': job_title,
                    'company': job_company,
                    'experience': job_experience
                },
                'profile_complete': False,
                'is_admin': False,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            database.child('users').child(uid).set(user_data)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('user.login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
            return render_template('user/register.html')
    return render_template('user/register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            # Get all users and filter them in Python
            all_users = database.child('users').get()
            
            if not all_users:
                flash('No users found. Please register first.', 'warning')
                return render_template('user/login.html')
            
            # all_users is a dictionary with user_id as keys and user_data as values
            user_found = False
            for user_id, user_data in all_users.items():
                # Check if this is the user we're looking for
                if user_data and user_data.get('email') == email:
                    user_found = True
                    if user_data.get('password') == password:
                        # Make sure user_data contains its own ID
                        if 'id' not in user_data:
                            user_data['id'] = user_id
                        
                        # If user is admin, ensure profile is marked as complete
                        if user_data.get('is_admin', False) and not user_data.get('profile_complete', False):
                            database.child('users').child(user_id).update({'profile_complete': True})
                            user_data['profile_complete'] = True
                        
                        user = User(user_id, user_data)
                        login_user(user)
                        flash('Logged in successfully!', 'success')
                        
                        # Redirect admin users directly to admin dashboard
                        if user_data.get('is_admin', False):
                            return redirect(url_for('admin.dashboard'))
                        return redirect(url_for('user.dashboard'))
                    else:
                        flash('Invalid password', 'danger')
                        return render_template('user/login.html')
            
            if not user_found:
                flash('No user found with that email. Please register first.', 'warning')
            else:
                flash('Invalid credentials', 'danger')
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')
    
    return render_template('user/login.html')

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user profile data
    user_data = database.child('users').child(current_user.id).get()
    
    # Make sure user_data has the ID field
    if user_data and 'id' not in user_data:
        user_data['id'] = current_user.id
    
    return render_template('user/dashboard.html', user=user_data)

@user_bp.route('/chat')
@login_required
def chat():
    # Get user profile data
    user_data = database.child('users').child(current_user.id).get()
    
    # Make sure user_data has the ID field
    if user_data and 'id' not in user_data:
        user_data['id'] = current_user.id
    
    # Get admin chat messages
    chat_messages_ref = database.child('admin_chat').get()
    chat_messages = chat_messages_ref if chat_messages_ref else {}
    
    # Filter messages for current user
    user_messages = {}
    if chat_messages:
        for msg_id, msg in chat_messages.items():
            if msg.get('sender_id') == current_user.id or msg.get('receiver_id') == current_user.id:
                user_messages[msg_id] = msg
    
    return render_template('user/chat.html', user=user_data, chat_messages=user_messages)

@user_bp.route('/send_admin_message', methods=['POST'])
@login_required
def send_admin_message():
    try:
        message = request.form.get('message')
        if not message:
            return jsonify({'status': 'error', 'message': 'No message provided'}), 400
            
        # Find admin user by iterating through all users (avoid Firebase indexing issue)
        try:
            all_users = database.child('users').get()
            admin_id = None
            
            if all_users:
                for user_id, user_data in all_users.items():
                    if user_data and user_data.get('is_admin', False):
                        admin_id = user_id
                        break
            
            if not admin_id:
                print("Error: Admin user not found")
                return jsonify({'status': 'error', 'message': 'Admin user not found'}), 404
            
            # Create message data
            message_data = {
                'sender_id': current_user.id,
                'sender_name': current_user.fullname,
                'receiver_id': admin_id,
                'message': message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': False,
                'type': 'user_to_admin'
            }
            
            try:
                database.child('admin_chat').push(message_data)
                
                # Emit Socket.IO event to notify admin in real-time
                try:
                    socketio.emit('new_user_message', {
                        'sender_id': current_user.id,
                        'sender_name': current_user.fullname,
                        'receiver_id': admin_id,
                        'message': message,
                        'timestamp': message_data['timestamp'],
                        'is_read': False,
                        'type': 'user_to_admin'
                    }, room=admin_id)
                    print(f"Socket.IO event emitted to admin {admin_id} for message from user {current_user.id}")
                except Exception as socket_error:
                    print(f"Socket.IO error (non-critical): {str(socket_error)}")
                    # Continue even if socket emission fails
                
                return jsonify({'status': 'success', 'message': 'Message sent successfully'})
            except Exception as db_error:
                print(f"Database error: {str(db_error)}")
                return jsonify({'status': 'error', 'message': f'Database error: {str(db_error)}'}), 500
        except Exception as e:
            print(f"Error finding admin: {str(e)}")
            return jsonify({'status': 'error', 'message': f'Error finding admin: {str(e)}'}), 500
    except Exception as e:
        print(f"General error in send_admin_message: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        print("\nProcessing profile update...")
        matches_ref = database.child('matches')
        matches_data = matches_ref.get()
        print(f"Current matches in database: {len(matches_data) if matches_data else 0}")

        # Get form data
        fullname = request.form['fullname']
        gender = request.form['gender']
        age = request.form['age']
        location = request.form['location']
        about = request.form['about']
        phone = request.form['phone']
        
        # Handle profile picture upload
        profile_picture_url = None
        if 'profile_picture' in request.files and request.files['profile_picture'].filename:
            try:
                profile_image = request.files['profile_picture']
                
                # Validate file size (max 5MB)
                if len(profile_image.read()) > 5 * 1024 * 1024:
                    flash('Image size exceeds 5MB. Please choose a smaller image.', 'danger')
                    # Reset file pointer after reading
                    profile_image.seek(0)
                    return redirect(url_for('user.profile'))
                
                # Reset file pointer after validation
                profile_image.seek(0)
                
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in profile_image.filename and \
                   profile_image.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    
                    # Create a secure filename with user ID
                    filename = secure_filename(profile_image.filename)
                    filename = f"{current_user.id}_{filename}"
                    
                    # Convert to base64 for storage
                    image_data = profile_image.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    
                    # Store image data in database
                    profile_picture_url = f"data:image/{profile_image.filename.split('.')[-1]};base64,{base64_data}"
                    
                else:
                    flash('Invalid file format. Please upload a PNG, JPG, JPEG or GIF file.', 'danger')
                    return redirect(url_for('user.profile'))
            except Exception as e:
                flash(f'Error uploading profile picture: {str(e)}', 'danger')
                print(f"Error uploading profile picture: {e}")
                return redirect(url_for('user.profile'))

        # Get education details
        education_level = request.form.get('education_level', '')
        education_field = request.form.get('education_field', '')
        education_institute = request.form.get('education_institute', '')

        # Get job details (optional)
        job_title = request.form.get('job_title', '')
        job_company = request.form.get('job_company', '')
        job_experience = request.form.get('job_experience', '')

        # Convert job_experience to int if not empty
        if job_experience:
            try:
                job_experience = int(job_experience)
            except ValueError:
                job_experience = 0
        else:
            job_experience = 0

        # Get partner preferences
        pref_gender = request.form.get('pref_gender', '')
        pref_age_min = request.form.get('pref_age_min', '')
        pref_age_max = request.form.get('pref_age_max', '')
        pref_location = request.form.get('pref_location', '')
        pref_education = request.form.get('pref_education', '')

        # Update user data
        user_ref = database.child('users').child(current_user.id)
        user_data = user_ref.get()

        # Validate required fields (employment details not required)
        if not all([fullname, gender, age, location, phone, about]):
            flash('Please fill in all required personal information fields', 'error')
            return render_template('user/profile.html', user=current_user)

        # Validate partner preferences
        if not all([pref_age_min, pref_age_max, pref_location]):
            flash('Please fill in all required partner preference fields', 'error')
            return render_template('user/profile.html', user=current_user)

        # Validate age range
        try:
            min_age = int(pref_age_min)
            max_age = int(pref_age_max)
            if min_age > max_age:
                flash('Minimum preferred age cannot be greater than maximum preferred age', 'error')
                return render_template('user/profile.html', user=current_user)
        except ValueError:
            flash('Age values must be valid numbers', 'error')
            return render_template('user/profile.html', user=current_user)

        # Update user data
        updated_data = {
            'fullname': fullname,
            'gender': gender,
            'age': int(age),
            'location': location,
            'phone': phone,
            'about': about,
            'education': {
                'level': education_level,
                'field': education_field,
                'institute': education_institute
            },
            'job': {
                'title': job_title,
                'company': job_company,
                'experience': job_experience
            },
            'preferences': {
                'gender': pref_gender,
                'age_min': int(pref_age_min),
                'age_max': int(pref_age_max),
                'location': pref_location,
                'education': pref_education
            },
            'profile_complete': True
        }
        
        # Add profile picture to update data if available
        if profile_picture_url:
            updated_data['profile_picture'] = profile_picture_url
        
        # Update the user data
        user_ref.update(updated_data)
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/add_review', methods=['POST'])
@login_required
def add_review():
    try:
        # Get form data
        rating = int(request.form['rating'])
        comment = request.form['comment']
        
        # Create review object
        review = {
            'user_id': current_user.id,
            'user_name': current_user.fullname,
            'rating': rating,
            'comment': comment,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Generate unique review ID
        review_id = str(uuid.uuid4())
        
        # Save to database
        reviews_ref = database.child('reviews').child(review_id)
        reviews_ref.set(review)
        
        flash('Thank you for your review!', 'success')
    except Exception as e:
        print(f"Error adding review: {e}")
        flash('There was an error submitting your review. Please try again.', 'danger')
    
    return redirect(url_for('index'))

@user_bp.route('/delete_profile', methods=['POST'])
@login_required
def delete_profile():
    """Delete user profile."""
    try:
        user_id = current_user.id
        
        # Delete user's conversations
        conversations_ref = database.child('conversations')
        conversations_data = conversations_ref.get() or []
        
        for conv_data in conversations_data:
            conv_id = conv_data.key()
            conv_data = conv_data.val()
            participants = conv_data.get('participants', [])
            if user_id in participants:
                conversations_ref.child(conv_id).delete()
                
                # Delete associated messages
                messages_ref = database.child('messages').child(conv_id)
                messages_ref.delete()
        
        # Delete user account
        database.child('users').child(user_id).delete()
        
        # Logout user
        logout_user()
        flash('Your profile has been deleted successfully.', 'success')
        return redirect(url_for('user.register'))
        
    except Exception as e:
        flash(f'Error deleting profile: {str(e)}', 'danger')
        return redirect(url_for('user.profile'))
