from datetime import datetime
from backend.app import db

class CarbonFootprint(db.Model):
    """Model for tracking user's carbon footprint calculations."""
    __tablename__ = 'carbon_footprints'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    calculation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Energy Usage
    electricity_usage = db.Column(db.Float)  # in kWh
    gas_usage = db.Column(db.Float)  # in cubic meters
    
    # Transportation
    vehicle_miles = db.Column(db.Float)  # miles driven
    public_transport_miles = db.Column(db.Float)
    air_travel_miles = db.Column(db.Float)
    
    # Waste
    waste_recycled = db.Column(db.Float)  # in kg
    waste_landfill = db.Column(db.Float)  # in kg
    
    # Results
    total_emissions = db.Column(db.Float)  # in kg CO2
    
    def calculate_total_emissions(self):
        """Calculate total carbon emissions based on input values."""
        # Conversion factors (simplified for example)
        ELECTRICITY_FACTOR = 0.5  # kg CO2 per kWh
        GAS_FACTOR = 2.0  # kg CO2 per cubic meter
        VEHICLE_FACTOR = 0.4  # kg CO2 per mile
        PUBLIC_TRANSPORT_FACTOR = 0.14  # kg CO2 per mile
        AIR_TRAVEL_FACTOR = 0.25  # kg CO2 per mile
        LANDFILL_FACTOR = 0.5  # kg CO2 per kg waste

        self.total_emissions = (
            (self.electricity_usage or 0) * ELECTRICITY_FACTOR +
            (self.gas_usage or 0) * GAS_FACTOR +
            (self.vehicle_miles or 0) * VEHICLE_FACTOR +
            (self.public_transport_miles or 0) * PUBLIC_TRANSPORT_FACTOR +
            (self.air_travel_miles or 0) * AIR_TRAVEL_FACTOR +
            (self.waste_landfill or 0) * LANDFILL_FACTOR
        )
        
        return self.total_emissions

    def get_reduction_tips(self):
        """Generate personalized tips based on the user's carbon footprint."""
        tips = []
        
        if self.electricity_usage and self.electricity_usage > 250:
            tips.append("Consider switching to energy-efficient appliances and LED lighting")
            
        if self.vehicle_miles and self.vehicle_miles > 100:
            tips.append("Try carpooling or using public transportation for your daily commute")
            
        if self.waste_landfill and self.waste_landfill > 10:
            tips.append("Increase recycling and composting to reduce landfill waste")
            
        if not tips:
            tips.append("Great job! Keep maintaining your low carbon footprint")
            
        return tips

    def to_dict(self):
        """Convert carbon footprint data to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'calculation_date': self.calculation_date.isoformat(),
            'electricity_usage': self.electricity_usage,
            'gas_usage': self.gas_usage,
            'vehicle_miles': self.vehicle_miles,
            'public_transport_miles': self.public_transport_miles,
            'air_travel_miles': self.air_travel_miles,
            'waste_recycled': self.waste_recycled,
            'waste_landfill': self.waste_landfill,
            'total_emissions': self.total_emissions
        }

    def __repr__(self):
        return f'<CarbonFootprint {self.id} - User {self.user_id} - {self.calculation_date}>'
