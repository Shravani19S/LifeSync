from app import app, db  # Import app separately to ensure proper initialization

with app.app_context():
    db.create_all()

print("Database initialized successfully!")
