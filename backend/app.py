from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from backend.config import config

# Initialize extensions
db = SQLAlchemy()

def create_app(config_name='default'):
    """Application factory function to create and configure the Flask app."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from backend.routes.account_routes import account_bp
    from backend.routes.product_routes import product_bp
    from backend.routes.consultation_routes import consultation_bp
    from backend.routes.carbon_routes import carbon_bp
    from backend.routes.loyalty_routes import loyalty_bp
    
    app.register_blueprint(account_bp, url_prefix='/api/account')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(consultation_bp, url_prefix='/api/consultations')
    app.register_blueprint(carbon_bp, url_prefix='/api/carbon')
    app.register_blueprint(loyalty_bp, url_prefix='/api/loyalty')
    
    # Register error handlers
    from backend.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000)
