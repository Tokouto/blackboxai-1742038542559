from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from backend.app import db

class User(UserMixin, db.Model):
    """User model for storing user account information."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    consultations = db.relationship('Consultation', backref='user', lazy=True)
    loyalty_points = db.Column(db.Integer, default=0)
    carbon_footprints = db.relationship('CarbonFootprint', backref='user', lazy=True)

    def set_password(self, password):
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def add_loyalty_points(self, points):
        """Add loyalty points to the user's account."""
        self.loyalty_points += points
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'
