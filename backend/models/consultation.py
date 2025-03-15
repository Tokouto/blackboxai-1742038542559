from datetime import datetime
from backend.app import db

class Consultation(db.Model):
    """Model for consultation bookings."""
    __tablename__ = 'consultations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    def to_dict(self):
        """Convert consultation to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_type': self.service_type,
            'scheduled_date': self.scheduled_date.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'notes': self.notes
        }

    @staticmethod
    def get_user_consultations(user_id):
        """Get all consultations for a specific user."""
        return Consultation.query.filter_by(user_id=user_id).order_by(Consultation.scheduled_date.desc()).all()

    def update_status(self, new_status):
        """Update the consultation status."""
        valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        self.status = new_status
        db.session.commit()

    def __repr__(self):
        return f'<Consultation {self.id} - {self.service_type} - {self.status}>'
