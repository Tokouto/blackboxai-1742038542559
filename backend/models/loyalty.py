from datetime import datetime
from backend.app import db

class LoyaltyTransaction(db.Model):
    """Model for tracking loyalty points transactions."""
    __tablename__ = 'loyalty_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)  # Positive for earned, negative for spent
    transaction_type = db.Column(db.String(50), nullable=False)  # 'earned' or 'redeemed'
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'points': self.points,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

class LoyaltyReward(db.Model):
    """Model for available loyalty rewards."""
    __tablename__ = 'loyalty_rewards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points_required = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert reward to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'points_required': self.points_required,
            'is_active': self.is_active
        }

class RewardRedemption(db.Model):
    """Model for tracking reward redemptions."""
    __tablename__ = 'reward_redemptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('loyalty_rewards.id'), nullable=False)
    points_spent = db.Column(db.Integer, nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, completed, cancelled

    # Relationships
    reward = db.relationship('LoyaltyReward', backref='redemptions')

    def to_dict(self):
        """Convert redemption to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reward_id': self.reward_id,
            'reward_name': self.reward.name,
            'points_spent': self.points_spent,
            'redeemed_at': self.redeemed_at.isoformat(),
            'status': self.status
        }

    @staticmethod
    def get_user_redemptions(user_id):
        """Get all redemptions for a specific user."""
        return RewardRedemption.query.filter_by(user_id=user_id)\
            .order_by(RewardRedemption.redeemed_at.desc()).all()

    def __repr__(self):
        return f'<RewardRedemption {self.id} - User {self.user_id} - Reward {self.reward_id}>'
