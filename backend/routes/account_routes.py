from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from backend.app import db
from backend.models.user import User

account_bp = Blueprint('account', __name__)

@account_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()

    # Validate required fields
    required_fields = ['email', 'username', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'message': f'Please provide all required fields: {", ".join(required_fields)}'
        }), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'error': 'Email exists',
            'message': 'A user with this email already exists'
        }), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'error': 'Username exists',
            'message': 'This username is already taken'
        }), 400

    # Create new user
    user = User(
        email=data['email'],
        username=data['username']
    )
    user.set_password(data['password'])

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Registration failed',
            'message': str(e)
        }), 500

@account_bp.route('/login', methods=['POST'])
def login():
    """Log in a user."""
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({
            'error': 'Missing credentials',
            'message': 'Please provide both email and password'
        }), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({
            'message': 'Logged in successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }), 200
    
    return jsonify({
        'error': 'Invalid credentials',
        'message': 'Invalid email or password'
    }), 401

@account_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@account_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get the current user's profile."""
    return jsonify({
        'user': {
            'id': current_user.id,
            'email': current_user.email,
            'username': current_user.username,
            'loyalty_points': current_user.loyalty_points,
            'created_at': current_user.created_at.isoformat()
        }
    }), 200

@account_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update the current user's profile."""
    data = request.get_json()
    
    if 'username' in data:
        # Check if new username is already taken
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != current_user.id:
            return jsonify({
                'error': 'Username exists',
                'message': 'This username is already taken'
            }), 400
        current_user.username = data['username']

    if 'password' in data:
        current_user.set_password(data['password'])

    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'username': current_user.username
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Update failed',
            'message': str(e)
        }), 500

@account_bp.route('/profile', methods=['DELETE'])
@login_required
def delete_account():
    """Delete the current user's account."""
    try:
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        return jsonify({'message': 'Account deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Deletion failed',
            'message': str(e)
        }), 500
