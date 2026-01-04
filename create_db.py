from app import app, db
from extensions import db
from models.user import User

with app.app_context():
    db.create_all()
    print("Database created successfully ✅")
