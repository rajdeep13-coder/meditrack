"""
Entry point for the MediTrack application.

This script creates the Flask application instance using the application
factory pattern and starts the development server when run directly.
"""

from dotenv import load_dotenv
import os

# Load environment variables from a .env file when present (development convenience)
load_dotenv()

from app import create_app

# Create the application instance using the factory function
app = create_app()

if __name__ == '__main__':
    # Ensure the instance directory exists for the SQLite database
    os.makedirs('instance', exist_ok=True)
    app.run(debug=True, port=5000)
