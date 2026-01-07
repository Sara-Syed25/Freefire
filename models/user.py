from flask_login import UserMixin
from extensions import db
# from datatime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # role = db.Column(db.String(20), nullable=False)  
    role = role = db.Column(db.String(20), nullable=False, default="player")


    wallet_balance = db.Column(db.Float, default=0.0)
    is_verified = db.Column(db.Boolean, default=False)

    otp_code = db.Column(db.String(6))
    # otp_expires_at = db.Column(db.DateTime)
    # is_verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.username}>"
