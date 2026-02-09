from app import app, db
from database.db import StudentPreference

with app.app_context():
    db.create_all()
    print("Student preferences table created successfully!")
