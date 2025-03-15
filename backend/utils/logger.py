import logging
import sys
from logging.handlers import RotatingFileHandler
from flask import request, has_request_context

class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request information."""
    
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.method = request.method
            record.remote_addr = request.remote_addr
            record.user_agent = request.user_agent.string
        else:
            record.url = None
            record.method = None
            record.remote_addr = None
            record.user_agent = None
            
        return super().format(record)

def setup_logger(app):
    """Configure application logging."""
    
    # Set log format
    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s - %(method)s %(url)s\n'
        '%(levelname)s: %(message)s\n'
        'User-Agent: %(user_agent)s\n'
        '--------------------------------------------------------------------------------'
    )
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configure file handler with rotation
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Log Flask errors
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        return 'Internal Server Error', 500
    
    # Log all requests
    @app.before_request
    def log_request_info():
        app.logger.info('Request Headers: %s', dict(request.headers))
        app.logger.info('Request Body: %s', request.get_data())
    
    # Log all responses
    @app.after_request
    def log_response_info(response):
        app.logger.info('Response Status: %s', response.status)
        app.logger.info('Response Headers: %s', dict(response.headers))
        return response
    
    return app

def get_logger(name):
    """Get a logger instance with the given name."""
    logger = logging.getLogger(name)
    return logger
