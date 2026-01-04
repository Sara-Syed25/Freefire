from extensions import db
from datetime import datetime

class WithdrawalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(20), default="pending")
    # pending / approved / rejected / paid

    requested_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Withdrawal user={self.user_id} amount={self.amount}>"
