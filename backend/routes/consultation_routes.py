from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.app import db
from backend.models.consultation import Consultation
from backend.models.user import User

consultation_bp = Blueprint('consultation', __name__)

@consultation_bp.route('/', methods=['POST'])
@login_required
def book_consultation():
    """Book a new consultation."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['service_type', 'scheduled_date']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'message': f'Please provide all required fields: {", ".join(required_fields)}'
        }), 400
    
    try:
        # Parse and validate the scheduled date
        scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
        if scheduled_date < datetime.utcnow():
            return jsonify({
                'error': 'Invalid date',
                'message': 'Consultation date must be in the future'
            }), 400
        
        # Create new consultation
        consultation = Consultation(
            user_id=current_user.id,
            service_type=data['service_type'],
            scheduled_date=scheduled_date,
            notes=data.get('notes', '')
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        # Add loyalty points for booking
        current_user.add_loyalty_points(10)  # Award 10 points for booking
        
        return jsonify({
            'message': 'Consultation booked successfully',
            'consultation': consultation.to_dict(),
            'loyalty_points_earned': 10
        }), 201
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid date format',
            'message': 'Please provide the date in ISO format (YYYY-MM-DDTHH:MM:SS)'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Booking failed',
            'message': str(e)
        }), 500

@consultation_bp.route('/', methods=['GET'])
@login_required
def get_consultations():
    """Get all consultations for the current user."""
    consultations = Consultation.get_user_consultations(current_user.id)
    return jsonify({
        'consultations': [consultation.to_dict() for consultation in consultations]
    }), 200

@consultation_bp.route('/<int:consultation_id>', methods=['GET'])
@login_required
def get_consultation(consultation_id):
    """Get a specific consultation."""
    consultation = Consultation.query.get_or_404(consultation_id)
    
    # Ensure user can only access their own consultations
    if consultation.user_id != current_user.id:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'You do not have permission to view this consultation'
        }), 403
    
    return jsonify(consultation.to_dict()), 200

@consultation_bp.route('/<int:consultation_id>', methods=['PUT'])
@login_required
def update_consultation(consultation_id):
    """Update a specific consultation."""
    consultation = Consultation.query.get_or_404(consultation_id)
    
    # Ensure user can only update their own consultations
    if consultation.user_id != current_user.id:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'You do not have permission to update this consultation'
        }), 403
    
    data = request.get_json()
    
    try:
        if 'scheduled_date' in data:
            scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
            if scheduled_date < datetime.utcnow():
                return jsonify({
                    'error': 'Invalid date',
                    'message': 'Consultation date must be in the future'
                }), 400
            consultation.scheduled_date = scheduled_date
        
        if 'service_type' in data:
            consultation.service_type = data['service_type']
        
        if 'notes' in data:
            consultation.notes = data['notes']
        
        if 'status' in data:
            consultation.update_status(data['status'])
        
        db.session.commit()
        return jsonify({
            'message': 'Consultation updated successfully',
            'consultation': consultation.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid data',
            'message': str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Update failed',
            'message': str(e)
        }), 500

@consultation_bp.route('/<int:consultation_id>', methods=['DELETE'])
@login_required
def cancel_consultation(consultation_id):
    """Cancel a specific consultation."""
    consultation = Consultation.query.get_or_404(consultation_id)
    
    # Ensure user can only cancel their own consultations
    if consultation.user_id != current_user.id:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'You do not have permission to cancel this consultation'
        }), 403
    
    try:
        consultation.update_status('cancelled')
        return jsonify({
            'message': 'Consultation cancelled successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Cancellation failed',
            'message': str(e)
        }), 500

@consultation_bp.route('/available-slots', methods=['GET'])
def get_available_slots():
    """Get available consultation time slots."""
    # This is a simplified version. In a real application, you would:
    # 1. Check the calendar for existing bookings
    # 2. Consider business hours
    # 3. Account for consultant availability
    # 4. Handle different time zones
    
    # For now, we'll return some dummy available slots
    available_slots = [
        {
            'date': (datetime.utcnow().replace(hour=9, minute=0) \
                    .strftime('%Y-%m-%dT%H:%M:%S')),
            'duration': 60,  # minutes
            'available': True
        },
        {
            'date': (datetime.utcnow().replace(hour=14, minute=0) \
                    .strftime('%Y-%m-%dT%H:%M:%S')),
            'duration': 60,  # minutes
            'available': True
        }
    ]
    
    return jsonify({
        'available_slots': available_slots
    }), 200
