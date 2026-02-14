"""
Setup script to initialize the database and check configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_environment():
    """Check if environment variables are configured"""
    print("=== Checking Environment Configuration ===\n")

    database_url = os.getenv("DATABASE_URL")
    api_key = os.getenv("API_KEY")

    if not database_url:
        print("⚠ WARNING: DATABASE_URL not set")
        print("  Using default SQLite database: sqlite:///./test.db")
    else:
        print(f"✓ DATABASE_URL configured")
        # Don't print the full URL for security
        if database_url.startswith("postgresql"):
            print("  Database type: PostgreSQL")
        elif database_url.startswith("sqlite"):
            print("  Database type: SQLite")

    if not api_key or api_key == "dev-key-change-in-production":
        print("\n⚠ WARNING: API_KEY not set or using default")
        print("  Please set a secure API key in .env file")
    else:
        print("✓ API_KEY configured")

    print("\n=== Initializing Database ===\n")

    try:
        from api.database import init_db, engine
        from api.models import SensorData

        # Create all tables
        init_db()
        print("✓ Database tables created successfully")

        # Test connection
        with engine.connect() as conn:
            print("✓ Database connection successful")

    except Exception as e:
        print(f"✗ Error initializing database: {str(e)}")
        return False

    print("\n=== Setup Complete ===\n")
    print("Next steps:")
    print("1. Start local server: python main.py")
    print("2. View API docs: http://localhost:8000/docs")
    print("3. Configure ESP32 with your API endpoint and key")
    print("\nFor Vercel deployment:")
    print("1. Install Vercel CLI: npm install -g vercel")
    print("2. Deploy: vercel")
    print("3. Set environment variables in Vercel dashboard")

    return True

if __name__ == "__main__":
    check_environment()
