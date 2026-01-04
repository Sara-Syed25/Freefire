from extensions import db

class LobbyParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    lobby_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<LobbyParticipant lobby={self.lobby_id} user={self.user_id}>"
