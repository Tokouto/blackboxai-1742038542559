from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.app import db
from backend.models.carbon_calc import CarbonFootprint

carbon_bp = Blueprint('carbon', __name__)

@carbon_bp.route('/calculate', methods=['POST'])
@login_required
def calculate_footprint():
    """Calculate and save a new carbon footprint entry."""
    data = request.get_json()
    
    # Create new carbon footprint entry
    footprint = CarbonFootprint(
        user_id=current_user.id,
        electricity_usage=data.get('electricity_usage'),
        gas_usage=data.get('gas_usage'),
        vehicle_miles=data.get('vehicle_miles'),
        public_transport_miles=data.get('public_transport_miles'),
        air_travel_miles=data.get('air_travel_miles'),
        waste_recycled=data.get('waste_recycled'),
        waste_landfill=data.get('waste_landfill')
    )
    
    try:
        # Calculate total emissions
        total_emissions = footprint.calculate_total_emissions()
        
        # Get personalized reduction tips
        reduction_tips = footprint.get_reduction_tips()
        
        # Save to database
        db.session.add(footprint)
        db.session.commit()
        
        # Award loyalty points for calculating carbon footprint
        current_user.add_loyalty_points(5)  # Award 5 points for participation
        
        return jsonify({
            'message': 'Carbon footprint calculated successfully',
            'total_emissions': total_emissions,
            'reduction_tips': reduction_tips,
            'loyalty_points_earned': 5,
            'footprint': footprint.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Calculation failed',
            'message': str(e)
        }), 500

@carbon_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    """Get carbon footprint history for the current user."""
    try:
        footprints = CarbonFootprint.query\
            .filter_by(user_id=current_user.id)\
            .order_by(CarbonFootprint.calculation_date.desc())\
            .all()
        
        return jsonify({
            'history': [footprint.to_dict() for footprint in footprints]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve history',
            'message': str(e)
        }), 500

@carbon_bp.route('/latest', methods=['GET'])
@login_required
def get_latest():
    """Get the user's most recent carbon footprint calculation."""
    try:
        latest_footprint = CarbonFootprint.query\
            .filter_by(user_id=current_user.id)\
            .order_by(CarbonFootprint.calculation_date.desc())\
            .first()
        
        if not latest_footprint:
            return jsonify({
                'message': 'No carbon footprint calculations found'
            }), 404
        
        return jsonify(latest_footprint.to_dict()), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve latest calculation',
            'message': str(e)
        }), 500

@carbon_bp.route('/average', methods=['GET'])
@login_required
def get_average():
    """Get the user's average carbon footprint over time."""
    try:
        footprints = CarbonFootprint.query\
            .filter_by(user_id=current_user.id)\
            .all()
        
        if not footprints:
            return jsonify({
                'message': 'No carbon footprint calculations found'
            }), 404
        
        total_emissions = sum(fp.total_emissions for fp in footprints)
        average_emissions = total_emissions / len(footprints)
        
        return jsonify({
            'average_emissions': average_emissions,
            'total_calculations': len(footprints)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to calculate average',
            'message': str(e)
        }), 500

@carbon_bp.route('/tips', methods=['GET'])
def get_general_tips():
    """Get general carbon footprint reduction tips."""
    tips = [
        {
            'category': 'Energy',
            'tips': [
                'Switch to LED light bulbs',
                'Use a programmable thermostat',
                'Seal air leaks around windows and doors',
                'Use energy-efficient appliances'
            ]
        },
        {
            'category': 'Transportation',
            'tips': [
                'Use public transportation when possible',
                'Consider carpooling',
                'Maintain proper tire pressure',
                'Combine errands into one trip'
            ]
        },
        {
            'category': 'Waste',
            'tips': [
                'Start composting food waste',
                'Recycle paper, plastic, and glass',
                'Use reusable bags and containers',
                'Avoid single-use plastics'
            ]
        },
        {
            'category': 'Lifestyle',
            'tips': [
                'Eat more plant-based meals',
                'Support local businesses',
                'Use cold water for laundry when possible',
                'Plant trees or start a garden'
            ]
        }
    ]
    
    return jsonify({'tips': tips}), 200
