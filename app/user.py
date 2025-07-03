from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from app import login_manager, database
import firebase_admin
from firebase_admin import db, storage
import uuid
from datetime import datetime
import pandas as pd
import os
import base64
from werkzeug.utils import secure_filename

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
    user_data = database.child('users').child(user_id).get()
    if user_data:
        # For Realtime Database, get() returns the actual data directly
        if 'id' not in user_data:
            user_data['id'] = user_id
        return User(user_id, user_data)
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

@user_bp.route('/delete_profile', methods=['POST'])
@login_required
def delete_profile():
    try:
        user_id = current_user.id
        
        # Delete user's conversations and messages
        conversations_ref = database.child('conversations')
        conversations_data = conversations_ref.get()
        for conv_data in conversations_data:
            conv_id = conv_data.key()
            conv_data = conv_data.val()
            participants = conv_data.get('participants', [])
            if user_id in participants:
                conversations_ref.child(conv_id).remove()
                
                # Delete associated messages
                messages_ref = database.child('messages').child(conv_id)
                messages_ref.remove()
        
        # Delete user account
        database.child('users').child(user_id).remove()
        
        # Logout user
        logout_user()
        flash('Your profile has been deleted successfully.', 'success')
        return redirect(url_for('user.register'))
        
    except Exception as e:
        flash(f'Error deleting profile: {str(e)}', 'danger')
        return redirect(url_for('user.profile'))

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

@user_bp.route('/messages')
@user_bp.route('/messages/<contact_id>')
@login_required
def messages(contact_id=None):
    try:
        # Get all conversations for the current user
        conversations_ref = database.child('conversations')
        conversations_data = conversations_ref.get()

        # Filter conversations involving the current user
        user_conversations = []
        current_contact = None
        chat_messages = []

        if conversations_data:
            for conv_id, conv_data in conversations_data.items():
                participants = conv_data.get('participants', [])
                if current_user.id in participants:
                    try:
                        # Get the other participant
                        other_id = [p for p in participants if p != current_user.id][0]

                        # Get user data for the other participant
                        other_user_ref = database.child('users').child(other_id)
                        other_user_data = other_user_ref.get()
                        
                        if not other_user_data:
                            continue
                        
                        # Create conversation object
                        conversation = {
                            'id': conv_id,
                            'other_user': {
                                'id': other_id,
                                'name': other_user_data.get('fullname', 'Unknown User'),
                                'profile_pic': other_user_data.get('profile_pic', '')
                            },
                            'last_message': conv_data.get('last_message', ''),
                            'last_time': conv_data.get('last_time', '')
                        }
                        
                        user_conversations.append(conversation)
                        
                        # If this is the selected conversation
                        if contact_id and other_id == contact_id:
                            current_contact = conversation['other_user']
                            
                            # Get messages for this conversation
                            messages_ref = database.child('messages').child(conv_id)
                            messages_data = messages_ref.get()
                            
                            if messages_data:
                                for msg_id, msg in messages_data.items():
                                    if isinstance(msg, dict):  # Make sure it's a valid message
                                        chat_messages.append(msg)
                            
                            # Sort messages by timestamp
                            chat_messages.sort(key=lambda x: x.get('timestamp', ''))
                    
                    except Exception as e:
                        print(f"Error processing conversation: {e}")
                        continue
        
        return render_template(
            'user/messages.html',
            conversations=user_conversations,
            current_contact=current_contact,
            messages=chat_messages
        )
    
    except Exception as e:
        flash(f"Error loading messages: {str(e)}", 'danger')
        return redirect(url_for('user.dashboard'))

@user_bp.route('/send_message/<recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    message_content = request.form.get('message')

    if not message_content and request.method == 'POST':
        flash('Message cannot be empty', 'danger')
        return redirect(url_for('user.messages'))

    # If it's a GET request, create a new conversation if needed and redirect to messages
    if request.method == 'GET':
        # Check if this is a new conversation
        conversations_ref = database.child('conversations')
        conversations_data = conversations_ref.get()

        conversation_id = None
        is_new_conversation = True

        # Look for existing conversation
        if conversations_data:
            for conv_id, conv_data in conversations_data.items():
                participants = conv_data.get('participants', [])
                if current_user.id in participants and recipient_id in participants:
                    conversation_id = conv_id
                    is_new_conversation = False
                    break

        # Create new conversation if needed
        if is_new_conversation:
            conversation_id = str(uuid.uuid4())
            conversation_data = {
                'participants': [current_user.id, recipient_id],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_message': '',
                'last_time': ''
            }
            conversations_ref.child(conversation_id).set(conversation_data)

        return redirect(url_for('user.messages', contact_id=recipient_id))

    # Handle POST request (sending a message)
    try:
        # Find conversation ID
        conversations_ref = database.child('conversations')
        conversations_data = conversations_ref.get()
        
        conversation_id = None
        
        if conversations_data:
            for conv_id, conv_data in conversations_data.items():
                participants = conv_data.get('participants', [])
                if current_user.id in participants and recipient_id in participants:
                    conversation_id = conv_id
                    break
        
        if not conversation_id:
            # Create new conversation
            conversation_id = str(uuid.uuid4())
            conversation_data = {
                'participants': [current_user.id, recipient_id],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_message': message_content,
                'last_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            conversations_ref.child(conversation_id).set(conversation_data)
        else:
            # Update last message and time
            conversations_ref.child(conversation_id).update({
                'last_message': message_content,
                'last_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Make sure conversation messages node exists
        conv_messages_ref = database.child('messages').child(conversation_id)
        conv_messages_data = conv_messages_ref.get()
        if conv_messages_data is None:
            conv_messages_ref.set({})
        
        # Create message
        message_id = str(uuid.uuid4())
        message_data = {
            'sender_id': current_user.id,
            'sender_name': current_user.fullname,
            'content': message_content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'read': False
        }
        
        # Save message
        conv_messages_ref.child(message_id).set(message_data)
        
        return redirect(url_for('user.messages', contact_id=recipient_id))
    
    except Exception as e:
        flash(f"Error sending message: {str(e)}", 'danger')
        return redirect(url_for('user.messages'))