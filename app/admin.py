from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from app import login_manager, database
import firebase_admin
from firebase_admin import db
import pandas as pd
import io
import uuid
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def require_admin():
    if request.endpoint not in ['admin.login', 'admin.register'] and (not current_user.is_authenticated or not getattr(current_user, 'is_admin', False)):
        return redirect(url_for('admin.login'))

@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Check if any admin exists
    admin_users = database.child('users').get()
    admin_exists = False
    
    if admin_users:
        for uid, user in admin_users.items():
            if user.get('is_admin', False):
                admin_exists = True
                break
    
    if admin_exists:
        flash('Admin account already exists. Please login.', 'warning')
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        fullname = request.form['fullname']
        
        # Check if email already exists
        existing_users = database.child('users').get()
        email_exists = False
        
        if existing_users:
            for uid, user in existing_users.items():
                if user.get('email') == email:
                    email_exists = True
                    break
        
        if email_exists:
            flash('Email already registered', 'danger')
            return render_template('admin/register.html')
        
        # Create new admin user
        uid = str(uuid.uuid4())
        new_user = {
            'id': uid,
            'email': email,
            'password': password,
            'fullname': fullname,
            'is_admin': True,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to database
        database.child('users').child(uid).set(new_user)
        
        flash('Admin account created successfully! Please login.', 'success')
        return redirect(url_for('admin.login'))
    
    return render_template('admin/register.html')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Check if any admin exists
    admin_users = database.child('users').get()
    admin_exists = False
    
    if admin_users:
        for uid, user in admin_users.items():
            if user.get('is_admin', False):
                admin_exists = True
                break
    
    if not admin_exists:
        flash('No admin account exists. Please create one.', 'warning')
        return redirect(url_for('admin.register'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        users = database.child('users').get()
        
        if users:
            for uid, user_data in users.items():
                if user_data.get('email') == email and user_data.get('is_admin', False) and user_data.get('password') == password:
                    user = UserMixin()
                    user.id = uid
                    user.email = email
                    user.is_admin = True
                    login_user(user)
                    flash('Admin login successful!', 'success')
                    return redirect(url_for('admin.dashboard'))
        flash('Invalid admin credentials', 'danger')
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Get all users
    users_ref = database.child('users').get()
    users = users_ref if users_ref else {}
    
    # Get all matches
    matches_ref = database.child('matches').get()
    matches = matches_ref if matches_ref else {}
    
    # Get all unique job titles for filter options
    job_titles = set()
    education_levels = set()
    for uid, user in users.items():
        if user.get('is_admin', False):
            continue
        # Get job titles
        if user.get('job') and user.get('job').get('title'):
            job_titles.add(user.get('job').get('title').lower())
        # Get education levels
        if user.get('education') and user.get('education').get('level'):
            education_levels.add(user.get('education').get('level'))
    
    # Sort the job titles and education levels
    job_titles = sorted(job_titles)
    education_levels = sorted(education_levels)
    
    # Find potential matches based on gender preferences
    potential_matches = find_potential_matches(users, matches)
    
    # Debug logging
    print('\nUsers:', len(users))
    print('Matches:', len(matches))
    print('Potential Matches:', len(potential_matches))
    if matches:
        print('\nMatch details:')
        for mid, match in matches.items():
            print(f'\nMatch ID: {mid}')
            print(f'Match data: {match}')
            if isinstance(match, dict):
                print(f'User1: {users.get(match.get("user1_id", ""), {}).get("fullname", "Unknown")}')
                print(f'User2: {users.get(match.get("user2_id", ""), {}).get("fullname", "Unknown")}')
                print(f'Score: {match.get("match_score", "N/A")}')
                print(f'Status: {match.get("status", "N/A")}')
            else:
                print(f'Unexpected match data type: {type(match)}')
    
    # Ensure matches is a dictionary of dictionaries
    valid_matches = {}
    for mid, match in matches.items():
        if isinstance(match, dict) and 'user1_id' in match and 'user2_id' in match:
            valid_matches[mid] = match
        else:
            print(f'Skipping invalid match {mid}: {match}')
    
    return render_template('admin/dashboard.html', users=users, matches=valid_matches, 
                           job_titles=job_titles, education_levels=education_levels,
                           potential_matches=potential_matches)

def find_potential_matches(users, existing_matches):
    """Find all potential male-female matches."""
    potential_matches = []
    
    # Extract existing match pairs to avoid duplicates
    existing_pairs = set()
    for match_id, match in existing_matches.items():
        if isinstance(match, dict) and 'user1_id' in match and 'user2_id' in match:
            user1_id = match.get('user1_id')
            user2_id = match.get('user2_id')
            existing_pairs.add((user1_id, user2_id))
            existing_pairs.add((user2_id, user1_id))  # Add reverse pair too
    
    # Group users by gender
    male_users = {}
    female_users = {}
    
    for uid, user in users.items():
        if user.get('is_admin', False):
            continue
            
        gender = user.get('gender', '').lower()
        if gender == 'male':
            male_users[uid] = user
        elif gender == 'female':
            female_users[uid] = user
    
    # Find all possible male-female combinations
    for male_id, male_user in male_users.items():
        for female_id, female_user in female_users.items():
            # Skip if this pair already exists in matches
            if (male_id, female_id) in existing_pairs:
                continue
                
            # Include all possible male-female combinations
            potential_matches.append({
                'male_id': male_id,
                'male_name': male_user.get('fullname', 'Unknown'),
                'female_id': female_id,
                'female_name': female_user.get('fullname', 'Unknown')
            })
    
    return potential_matches

@admin_bp.route('/download_xls')
@login_required
def download_xls():
    # Get users and matches data
    users_ref = database.child('users').get()
    users = users_ref if users_ref else {}
    
    matches_ref = database.child('matches').get()
    matches = matches_ref if matches_ref else {}
    
    # Get filter parameters
    job_filter = request.args.get('job', '').lower()
    education_filter = request.args.get('education', '').lower()
    
    # Prepare users data (excluding admins)
    users_data = []
    for uid, user in users.items():
        if user.get('is_admin', False):
            continue
        
        # Get education and job details
        education = user.get('education', {}) or {}
        job = user.get('job', {}) or {}
        preferences = user.get('preferences', {}) or {}
        
        # Apply filters if specified
        if job_filter and (not job.get('title') or job.get('title', '').lower() != job_filter):
            continue
            
        if education_filter and (not education.get('level') or education.get('level', '').lower() != education_filter):
            continue
            
        user_data = {
            'Full Name': user.get('fullname', ''),
            'Gender': user.get('gender', ''),
            'Age': user.get('age', ''),
            'Location': user.get('location', ''),
            'Phone': user.get('phone', ''),
            'Profile Complete': 'Yes' if user.get('profile_complete', False) else 'No',
            # Education details
            'Education Level': education.get('level', ''),
            'Field of Study': education.get('field', ''),
            'Institution': education.get('institute', ''),
            # Job details
            'Job Title': job.get('title', ''),
            'Company': job.get('company', ''),
            'Experience (Years)': job.get('experience', ''),
            # Partner Preferences
            'Pref Age Min': preferences.get('age_min', ''),
            'Pref Age Max': preferences.get('age_max', ''),
            'Pref Location': preferences.get('location', ''),
            'Pref Education Level': preferences.get('education_level', ''),
            'Pref Education Field': preferences.get('education_field', ''),
            'Pref Job Title': preferences.get('job_title', ''),
            'Pref Min Experience': preferences.get('min_experience', ''),
            'Pref Qualities': preferences.get('qualities', '')
        }
        users_data.append(user_data)
    
    # Prepare matches data
    matches_data = []
    for match_id, match in matches.items():
        user1_id = match.get('user1_id', '')
        user2_id = match.get('user2_id', '')
        user1 = users.get(user1_id, {})
        user2 = users.get(user2_id, {})
        
        # Get job and education details for both users
        user1_job = user1.get('job', {}) or {}
        user2_job = user2.get('job', {}) or {}
        user1_edu = user1.get('education', {}) or {}
        user2_edu = user2.get('education', {}) or {}
        
        # Apply filters if specified for matches
        if job_filter:
            job1_match = user1_job.get('title', '').lower() and job_filter in user1_job.get('title', '').lower()
            job2_match = user2_job.get('title', '').lower() and job_filter in user2_job.get('title', '').lower()
            if not (job1_match or job2_match):
                continue
                
        if education_filter:
            edu1_match = user1_edu.get('level', '').lower() == education_filter
            edu2_match = user2_edu.get('level', '').lower() == education_filter
            if not (edu1_match or edu2_match):
                continue
        
        match_data = {
            'Male': user1.get('fullname', ''),
            'Male Phone': user1.get('phone', ''),
            'Male Job': user1_job.get('title', ''),
            'Male Company': user1_job.get('company', ''),
            'Male Education': user1_edu.get('level', ''),
            'Female': user2.get('fullname', ''),
            'Female Phone': user2.get('phone', ''),
            'Female Job': user2_job.get('title', ''),
            'Female Company': user2_job.get('company', ''),
            'Female Education': user2_edu.get('level', ''),
            'Match Score': match.get('match_score', ''),
            'Status': match.get('status', ''),
            'Match Date': match.get('match_date', '')
        }
        matches_data.append(match_data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    
    # Create a Pandas Excel writer using XlsxWriter as the engine
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Convert users data to DataFrame and write to Excel
        if users_data:
            users_df = pd.DataFrame(users_data)
            users_df.to_excel(writer, sheet_name='Users', index=False)
        else:
            pd.DataFrame().to_excel(writer, sheet_name='Users', index=False)
        
        # Convert matches data to DataFrame and write to Excel
        if matches_data:
            matches_df = pd.DataFrame(matches_data)
            matches_df.to_excel(writer, sheet_name='Matches', index=False)
        else:
            pd.DataFrame().to_excel(writer, sheet_name='Matches', index=False)
    
    # Set up the response
    output.seek(0)
    
    # Generate filename with filters
    filename = 'user_data'
    if job_filter:
        filename += f'_job_{job_filter}'
    if education_filter:
        filename += f'_edu_{education_filter}'
    filename += '.xlsx'
    
    # Use send_file with mimetype and additional headers to ensure proper download behavior
    response = send_file(
        output, 
        download_name=filename, 
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Add a header to encourage redirect after download
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Location"] = url_for('admin.dashboard')
    
    # Flash a message that will be shown when they return to the dashboard
    flash('Data downloaded successfully!', 'success')
    
    return response

@admin_bp.route('/create_match', methods=['POST'])
@login_required
def create_match():
    user1_id = request.form.get('user1_id')
    user2_id = request.form.get('user2_id')
    match_score = int(request.form.get('match_score', 0))
    
    if not user1_id or not user2_id:
        flash('Both users must be selected', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Check if users exist
    users = database.child('users').get()
    
    if not users or user1_id not in users or user2_id not in users:
        flash('One or both users do not exist', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Check if match already exists
    matches = database.child('matches').get() or {}
    
    for mid, match in matches.items():
        if (match.get('user1_id') == user1_id and match.get('user2_id') == user2_id) or \
           (match.get('user1_id') == user2_id and match.get('user2_id') == user1_id):
            flash('Match already exists between these users', 'warning')
            return redirect(url_for('admin.dashboard'))
    
    # Ensure user1 is Male and user2 is Female
    user1 = users.get(user1_id, {})
    user2 = users.get(user2_id, {})
    
    # If user1 is not male or user2 is not female, swap them
    if (user1.get('gender', '').lower() != 'male' or user2.get('gender', '').lower() != 'female'):
        if user1.get('gender', '').lower() == 'female' and user2.get('gender', '').lower() == 'male':
            # Swap user IDs
            user1_id, user2_id = user2_id, user1_id
        else:
            flash('Please select a male for the first user and a female for the second user', 'warning')
            return redirect(url_for('admin.dashboard'))
    
    # Create match
    match_id = str(uuid.uuid4())
    match_data = {
        'user1_id': user1_id,  # Male
        'user2_id': user2_id,  # Female
        'match_score': match_score,
        'status': 'pending',
        'match_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    database.child('matches').child(match_id).set(match_data)
    flash('Match created successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/update_match_status/<match_id>', methods=['POST'])
@login_required
def update_match_status(match_id):
    new_status = request.form.get('status')
    
    if not new_status:
        flash('Status is required', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Check if match exists
    match = database.child('matches').child(match_id).get()
    
    if not match:
        flash('Match not found', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Update match status
    database.child('matches').child(match_id).update({'status': new_status})
    flash('Match status updated', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete_match/<match_id>', methods=['POST'])
@login_required
def delete_match(match_id):
    # Check if match exists
    match = database.child('matches').child(match_id).get()
    
    if not match:
        flash('Match not found', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Delete match
    database.child('matches').child(match_id).remove()
    flash('Match deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/create_all_matches', methods=['POST'])
@login_required
def create_all_matches():
    """Create all possible male-female matches."""
    # Get all users
    users_ref = database.child('users').get()
    users = users_ref if users_ref else {}
    
    # Get existing matches
    matches_ref = database.child('matches').get()
    matches = matches_ref if matches_ref else {}
    
    # Find all potential matches
    potential_matches = find_potential_matches(users, matches)
    
    # Create matches for all potential pairs
    matches_created = 0
    for match in potential_matches:
        male_id = match['male_id']
        female_id = match['female_id']
        
        # Create match
        match_id = str(uuid.uuid4())
        match_data = {
            'user1_id': male_id,  # Male
            'user2_id': female_id,  # Female
            'match_score': 50,  # Default score
            'status': 'pending',
            'match_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        database.child('matches').child(match_id).set(match_data)
        matches_created += 1
    
    if matches_created > 0:
        flash(f'Successfully created {matches_created} new matches!', 'success')
    else:
        flash('No new matches to create.', 'info')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<user_id>', methods=['GET'])
@login_required
def view_user(user_id):
    """View detailed information about a specific user."""
    # Get user data
    user = database.child('users').child(user_id).get()
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin.dashboard'))
    
    # Get any matches this user is part of
    matches_ref = database.child('matches').get() or {}
    user_matches = []
    
    for match_id, match in matches_ref.items():
        if match.get('user1_id') == user_id or match.get('user2_id') == user_id:
            # Get the other user in this match
            other_user_id = match.get('user2_id') if match.get('user1_id') == user_id else match.get('user1_id')
            other_user = database.child('users').child(other_user_id).get() or {}
            
            user_matches.append({
                'match_id': match_id,
                'other_user': other_user,
                'other_user_id': other_user_id,
                'match_score': match.get('match_score', 0),
                'status': match.get('status', 'pending'),
                'match_date': match.get('match_date', '')
            })
    
    return render_template('admin/user_view.html', user=user, user_id=user_id, user_matches=user_matches)