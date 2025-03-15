from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.app import db
from backend.models.loyalty import LoyaltyTransaction, LoyaltyReward, RewardRedemption
from backend.models.user import User

loyalty_bp = Blueprint('loyalty', __name__)

@loyalty_bp.route('/points', methods=['GET'])
@login_required
def get_points():
    """Get the current user's loyalty points balance."""
    return jsonify({
        'points': current_user.loyalty_points,
        'user_id': current_user.id
    }), 200

@loyalty_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    """Get the user's loyalty points transaction history."""
    transactions = LoyaltyTransaction.query\
        .filter_by(user_id=current_user.id)\
        .order_by(LoyaltyTransaction.created_at.desc())\
        .all()
    
    return jsonify({
        'transactions': [transaction.to_dict() for transaction in transactions]
    }), 200

@loyalty_bp.route('/rewards', methods=['GET'])
def get_rewards():
    """Get all available loyalty rewards."""
    rewards = LoyaltyReward.query\
        .filter_by(is_active=True)\
        .all()
    
    return jsonify({
        'rewards': [reward.to_dict() for reward in rewards]
    }), 200

@loyalty_bp.route('/rewards/<int:reward_id>', methods=['GET'])
def get_reward(reward_id):
    """Get details of a specific reward."""
    reward = LoyaltyReward.query.get_or_404(reward_id)
    
    if not reward.is_active:
        return jsonify({
            'error': 'Reward not available',
            'message': 'This reward is no longer active'
        }), 404
    
    return jsonify(reward.to_dict()), 200

@loyalty_bp.route('/rewards/<int:reward_id>/redeem', methods=['POST'])
@login_required
def redeem_reward(reward_id):
    """Redeem a reward using loyalty points."""
    reward = LoyaltyReward.query.get_or_404(reward_id)
    
    if not reward.is_active:
        return jsonify({
            'error': 'Reward not available',
            'message': 'This reward is no longer active'
        }), 400
    
    if current_user.loyalty_points < reward.points_required:
        return jsonify({
            'error': 'Insufficient points',
            'message': f'You need {reward.points_required} points to redeem this reward'
        }), 400
    
    try:
        # Create redemption record
        redemption = RewardRedemption(
            user_id=current_user.id,
            reward_id=reward.id,
            points_spent=reward.points_required
        )
        db.session.add(redemption)
        
        # Deduct points from user
        current_user.loyalty_points -= reward.points_required
        
        # Record the transaction
        transaction = LoyaltyTransaction(
            user_id=current_user.id,
            points=-reward.points_required,
            transaction_type='redeemed',
            description=f'Redeemed reward: {reward.name}'
        )
        db.session.add(transaction)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Reward redeemed successfully',
            'redemption': redemption.to_dict(),
            'points_remaining': current_user.loyalty_points
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Redemption failed',
            'message': str(e)
        }), 500

@loyalty_bp.route('/redemptions', methods=['GET'])
@login_required
def get_redemptions():
    """Get the user's reward redemption history."""
    redemptions = RewardRedemption.get_user_redemptions(current_user.id)
    
    return jsonify({
        'redemptions': [redemption.to_dict() for redemption in redemptions]
    }), 200

# Admin routes for managing rewards
@loyalty_bp.route('/rewards', methods=['POST'])
@login_required
def create_reward():
    """Create a new loyalty reward (admin only)."""
    # TODO: Add proper admin check
    data = request.get_json()
    
    required_fields = ['name', 'points_required']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'message': f'Please provide all required fields: {", ".join(required_fields)}'
        }), 400
    
    reward = LoyaltyReward(
        name=data['name'],
        description=data.get('description'),
        points_required=data['points_required']
    )
    
    try:
        db.session.add(reward)
        db.session.commit()
        return jsonify(reward.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Creation failed',
            'message': str(e)
        }), 500

@loyalty_bp.route('/rewards/<int:reward_id>', methods=['PUT'])
@login_required
def update_reward(reward_id):
    """Update a loyalty reward (admin only)."""
    # TODO: Add proper admin check
    reward = LoyaltyReward.query.get_or_404(reward_id)
    data = request.get_json()
    
    if 'name' in data:
        reward.name = data['name']
    if 'description' in data:
        reward.description = data['description']
    if 'points_required' in data:
        reward.points_required = data['points_required']
    if 'is_active' in data:
        reward.is_active = data['is_active']
    
    try:
        db.session.commit()
        return jsonify(reward.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Update failed',
            'message': str(e)
        }), 500

@loyalty_bp.route('/rewards/<int:reward_id>', methods=['DELETE'])
@login_required
def delete_reward(reward_id):
    """Delete (deactivate) a loyalty reward (admin only)."""
    # TODO: Add proper admin check
    reward = LoyaltyReward.query.get_or_404(reward_id)
    reward.is_active = False
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Reward deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Deletion failed',
            'message': str(e)
        }), 500
