import os
from backend.app import create_app
from flask import send_from_directory

app = create_app()

# Serve frontend static files
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('frontend', path)):
        return send_from_directory('frontend', path)
    else:
        return send_from_directory('frontend', 'index.html')

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    # Run the application
    app.run(host='0.0.0.0', port=8000, debug=True)
