from extensions import db

class Lobby(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    match_type = db.Column(db.String(20), nullable=False)  
    # solo / duo / squad

    entry_fee = db.Column(db.Integer, nullable=False)
    kill_reward = db.Column(db.Integer, nullable=False)

    total_slots = db.Column(db.Integer, nullable=False)
    filled_slots = db.Column(db.Integer, default=0)

    status = db.Column(db.String(20), default="open")  
    # open / full / completed

    admin_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Lobby {self.name} - {self.match_type}>"
