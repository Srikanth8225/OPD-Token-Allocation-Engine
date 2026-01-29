"""
Run script for OPD Token Allocation Engine
"""
from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("OPD Token Allocation Engine")
    print("=" * 60)
    print("Starting Flask server...")
    print("API available at: http://localhost:5000/api")
    print("Health check: http://localhost:5000/api/health")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
