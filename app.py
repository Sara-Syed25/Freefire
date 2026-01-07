from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from flask import render_template, request, redirect, url_for, flash
# from models.user import User
# from app import db
from extensions import db, login_manager
from models import user
from models import lobby
from models.user import User
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models.lobby import Lobby
from models.lobby_participant import LobbyParticipant
from models.wallet_transaction import WalletTransaction
from models.withdrawal_request import WithdrawalRequest
from flask_jwt_extended import JWTManager
import random
def generate_otp():
    return str(random.randint(100000, 999999))

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key-change-this"
jwt = JWTManager(app)

# app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

@app.route("/")
def home():
    return "Free Fire Esports Platform Running 🚀"

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         email = request.form["email"]
#         raw_password = request.form["password"]
#         hashed_password = generate_password_hash(raw_password)


#         new_user = User(
#             username=username,
#             email=email,
#             password=hashed_password,
#             role="player"
#         )

#         db.session.add(new_user)
#         db.session.commit()

#         return "User registered successfully ✅"

#     return render_template("register.html")

# login
def load_user(user_id):
        return User.query.get(int(user_id))
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # login_user(user)
            # return redirect("/dashboard")
            login_user(user)

            if user.role == "admin":
                return redirect("/admin/dashboard")
            else:
                return redirect("/player/dashboard")


        return "Invalid email or password ❌"

    return render_template("login.html")



# DASHBOARDSSS
@app.route("/dashboard")
@login_required

# player dash
def dashboard():
    return f"Welcome {current_user.username}! Role: {current_user.role}"
@app.route("/player/dashboard")
@login_required
def player_dashboard():
    if current_user.role != "player":
        return "Access denied ❌"
      
    return render_template(
        "player_dashboard.html",
        balance=current_user.wallet_balance
    )

    # return f"""
    # <h2>Player Dashboard</h2>
    # <p>Welcome {current_user.username}</p>
    # <p>Wallet Balance: ₹{current_user.wallet_balance}</p>
    # <a href="/player/lobbies">View Available Lobbies</a>
    # """



# Admin Dashboard
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return "Access denied ❌"

    users = User.query.all()
    lobbies = Lobby.query.all()
    withdrawals = WithdrawalRequest.query.filter_by(status="pending").all()
    transactions = WalletTransaction.query.order_by(
        WalletTransaction.timestamp.desc()
    ).limit(10).all()

    total_wallet = sum(u.wallet_balance for u in users)

    return render_template(
        "admin_dashboard.html",
        users=users,
        lobbies=lobbies,
        withdrawals=withdrawals,
        transactions=transactions,
        total_wallet=total_wallet
    )



# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")




#ADMIN CREATES LOBBYY
@app.route("/admin/create-lobby", methods=["GET", "POST"])
@login_required
def create_lobby():
    if current_user.role != "admin":
        return "Access denied ❌"

    if request.method == "POST":
        name = request.form["name"]
        match_type = request.form["match_type"]
        entry_fee = int(request.form["entry_fee"])
        kill_reward = int(request.form["kill_reward"])
        total_slots = int(request.form["total_slots"])

        lobby = Lobby(
            name=name,
            match_type=match_type,
            entry_fee=entry_fee,
            kill_reward=kill_reward,
            total_slots=total_slots,
            admin_id=current_user.id
        )

        db.session.add(lobby)
        db.session.commit()

        return "Lobby created successfully ✅"

    return render_template("admin_create_lobby.html")

# PLAYER WILL SEE THE AVAILABLE LOBBIES
@app.route("/player/lobbies")
@login_required
def player_lobbies():
    if current_user.role != "player":
        return "Access denied ❌"

    lobbies = Lobby.query.filter_by(status="open").all()

    return render_template(
        "player_lobbies.html",
        lobbies=lobbies
    )

# ROUTE TO JOIN LOBBY
# if lobby is full, not open,if player has already joined,
@app.route("/player/join-lobby/<int:lobby_id>")
@login_required
def join_lobby(lobby_id):

    if current_user.role != "player":
        return "Access denied ❌"

    lobby = Lobby.query.get(lobby_id)

    if not lobby:
        return "Lobby not found ❌"

    if lobby.status != "open":
        return "Lobby is not open ❌"

    if lobby.filled_slots >= lobby.total_slots:
        lobby.status = "full"
        db.session.commit()
        return "Lobby is full ❌"

    existing = LobbyParticipant.query.filter_by(
        lobby_id=lobby.id,
        user_id=current_user.id
    ).first()

    if existing:
        return "You already joined this lobby ❌"

    # Check wallet balance
    if current_user.wallet_balance < lobby.entry_fee:
        return "Insufficient wallet balance ❌"

# Deduct entry fee
    current_user.wallet_balance -= lobby.entry_fee

    transaction = WalletTransaction(
        user_id=current_user.id,
        amount=lobby.entry_fee,
        transaction_type="debit",
        description=f"Joined lobby: {lobby.name}"
)

    participant = LobbyParticipant(
        lobby_id=lobby.id,
        user_id=current_user.id
)

    lobby.filled_slots += 1

    if lobby.filled_slots == lobby.total_slots:
        lobby.status = "full"

    db.session.add(transaction)
    db.session.add(participant)
    db.session.commit()


    # return "Joined lobby successfully ✅"
    return redirect("/player/dashboard")

# WALLET TOP UP
@app.route("/player/add-money/<int:amount>")
@login_required
def add_money(amount):
    if current_user.role != "player":
        return "Access denied ❌"

    current_user.wallet_balance += amount

    transaction = WalletTransaction(
        user_id=current_user.id,
        amount=amount,
        transaction_type="credit",
        description="Manual wallet top-up (dev)"
    )

    db.session.add(transaction)
    db.session.commit()

    return redirect("/player/dashboard")


# ADMIN PAGE-----TO VIEEW LOBBY PLAYERS
@app.route("/admin/lobby/<int:lobby_id>/participants")
@login_required
def lobby_participants(lobby_id):
    if current_user.role != "admin":
        return "Access denied ❌"

    lobby = Lobby.query.get(lobby_id)
    participants = LobbyParticipant.query.filter_by(lobby_id=lobby_id).all()

    return render_template(
        "admin_lobby_participants.html",
        lobby=lobby,
        participants=participants
    )


# CREDIT KILLS LOGIC
@app.route("/admin/credit-kills", methods=["POST"])
@login_required
def credit_kills():
    if current_user.role != "admin":
        return "Access denied ❌"

    user_id = int(request.form["user_id"])
    lobby_id = int(request.form["lobby_id"])
    kills = int(request.form["kills"])

    lobby = Lobby.query.get(lobby_id)
    user = User.query.get(user_id)

    reward = kills * lobby.kill_reward

    user.wallet_balance += reward

    transaction = WalletTransaction(
        user_id=user.id,
        amount=reward,
        transaction_type="credit",
        description=f"Kill reward from lobby: {lobby.name}"
    )

    db.session.add(transaction)
    db.session.commit()

    return redirect(f"/admin/lobby/{lobby_id}/participants")


# WITHDRAWAL REQUESTS of players
@app.route("/player/request-withdrawal", methods=["GET", "POST"])
@login_required
def request_withdrawal():
    if current_user.role != "player":
        return "Access denied ❌"

    if request.method == "POST":
        amount = float(request.form["amount"])

        if amount > current_user.wallet_balance:
            return "Insufficient balance ❌"

        withdrawal = WithdrawalRequest(
            user_id=current_user.id,
            amount=amount
        )

        current_user.wallet_balance -= amount

        db.session.add(withdrawal)
        db.session.commit()

        return redirect("/player/dashboard")

    return render_template("player_withdrawal.html")


# admin sees withdrawal requests

@app.route("/admin/withdrawals")
@login_required
def admin_withdrawals():
    if current_user.role != "admin":
        return "Access denied ❌"

    withdrawals = WithdrawalRequest.query.all()
    return render_template(
        "admin_withdrawals.html",
        withdrawals=withdrawals
    )


# admin approves withdrawl req
@app.route("/admin/approve-withdrawal/<int:wid>")
@login_required
def approve_withdrawal(wid):
    if current_user.role != "admin":
        return "Access denied ❌"

    withdrawal = WithdrawalRequest.query.get(wid)
    withdrawal.status = "approved"

    db.session.commit()
    return redirect("/admin/withdrawals")

# admin dashboard for transactions
@app.route("/admin/transactions")
@login_required
def admin_transactions():
    if current_user.role != "admin":
        return "Access denied ❌"

    transactions = WalletTransaction.query.order_by(
        WalletTransaction.timestamp.desc()
    ).all()

    users = {u.id: u.username for u in User.query.all()}

    return render_template(
        "admin_transactions.html",
        transactions=transactions,
        users=users
    )

from extensions import mail
from config import MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD

app.config.update(
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_USE_TLS=MAIL_USE_TLS,
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
)

mail.init_app(app)

from flask_mail import Message
from extensions import mail

def send_email(to, subject, body):
    msg = Message(
        subject=subject,
        recipients=[to],
        body=body,
        sender=("Free Fire Esports", "syedasara2506@gmail.com")
    )
    mail.send(msg)

# @app.route("/test-email")
# def test_email():
#     send_email(
#         # to="23f2001706@ds.study.iitm.ac.in",
#         to=user.email,
#         subject="SMTP Working",
#         body="Your Free Fire Esports platform email system works."
#     )
#     return "Email sent"

# if __name__ == "__main__":
#     app.run(debug=True)
from flask_jwt_extended import create_access_token

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         email = request.form["email"]
#         password = request.form["password"]

#         hashed_password = generate_password_hash(password)

#         user = User(
#             username=username,
#             email=email,
#             password=hashed_password
#         )

#         db.session.add(user)
#         db.session.commit()

#         # 🔐 Generate JWT token for THIS user
#         token = create_access_token(identity=user.id)

#         # 🔗 Verification link
#         verify_link = f"http://127.0.0.1:5000/verify-email/{token}"

#         # ✉️ SEND EMAIL TO THE REGISTERED USER
#         send_email(
#             to=user.email,   # 👈 AUTOMATIC
#             subject="Verify your Free Fire account",
#             body=f"""
# Welcome to Free Fire Esports!

# Click the link below to verify your account:
# {verify_link}

# If you did not register, ignore this email.
# """
#         )

#         return "Registration successful! Check your email to verify."

#     return render_template("register.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check email uniqueness
        if User.query.filter_by(email=email).first():
            return "Email already registered."

        hashed_password = generate_password_hash(password)

        otp = generate_otp()

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            role="player",
            wallet_balance=0.0,
            otp_code=otp,
            # otp_expires_at=datetime.utcnow() + timedelta(minutes=5),
            is_verified=False
        )

        db.session.add(user)
        db.session.commit()

        # Send OTP email
        send_email(
            to=user.email,
            subject="Your Free Fire OTP Verification Code",
            body=f"""
Welcome to Free Fire Esports!

Your OTP code is: {otp}

This OTP is valid for 5 minutes.
Do not share it with anyone.
"""
        )

        return redirect(url_for("verify_otp", user_id=user.id))

    return render_template("register.html")

# verification
from flask_jwt_extended import decode_token

@app.route("/verify-email/<token>")
def verify_email(token):
    data = decode_token(token)
    user_id = data["sub"]

    user = User.query.get(user_id)
    user.is_verified = True

    db.session.commit()

    return "Email verified successfully. You can now log in."



# otp
from datetime import datetime

@app.route("/verify-otp/<int:user_id>", methods=["GET", "POST"])
def verify_otp(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        otp = request.form["otp"]

        if user.is_verified:
            return "Account already verified."

        if user.otp_code != otp:
            return "Invalid OTP."

        # if datetime.utcnow() > user.otp_expires_at:
            # return "OTP expired. Please register again."

        # Success
        user.is_verified = True
        user.otp_code = None
        user.otp_expires_at = None

        db.session.commit()

        return "Account verified successfully. You can now login."

    return render_template("verify_otp.html")


if __name__ == "__main__":
    app.run(debug=True)
# from flask import render_template, request, redirect, url_for, flash
# from extensions import db, login_manager
# # removed duplicate/unused imports: from models import user, from models import lobby
# from models.user import User
# from werkzeug.security import generate_password_hash
# from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.security import check_password_hash
# from models.lobby import Lobby
# from models.lobby_participant import LobbyParticipant
# from models.wallet_transaction import WalletTransaction
# from models.withdrawal_request import WithdrawalRequest
# from flask_jwt_extended import create_access_token
# # ...existing code...
# @login_manager.user_loader
# def load_user(user_id):
#     try:
#         return User.query.get(int(user_id))
#     except Exception:
#         return None
# # ...existing code...
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form["username"]
#         email = request.form["email"]
#         raw_password = request.form["password"]
#         hashed_password = generate_password_hash(raw_password)

#         new_user = User(
#             username=username,
#             email=email,
#             password=hashed_password,
#             role="player"
#         )

#         try:
#             db.session.add(new_user)
#             db.session.commit()
#         except Exception as e:
#             db.session.rollback()
#             flash(f"Error registering user: {e}")
#             return redirect(url_for("register"))

#         # Generate JWT token and send verification email (non-blocking/simple)
#         try:
#             token = create_access_token(identity=new_user.id)
#             verify_link = f"http://127.0.0.1:5000/verify-email/{token}"
#             # send_email is defined below after mail.init_app
#             send_email(
#                 to=new_user.email,
#                 subject="Verify your Free Fire account",
#                 body=f"Welcome! Click to verify: {verify_link}"
#             )
#         except Exception:
#             # don't block registration on email errors
#             pass

#         return "Registration successful! Check your email to verify."

#     return render_template("register.html")
# # ...existing code...
# from extensions import mail
# from config import MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD

# app.config.update(
#     MAIL_SERVER=MAIL_SERVER,
#     MAIL_PORT=MAIL_PORT,
#     MAIL_USE_TLS=MAIL_USE_TLS,
#     MAIL_USERNAME=MAIL_USERNAME,
#     MAIL_PASSWORD=MAIL_PASSWORD,
# )

# mail.init_app(app)

# from flask_mail import Message

# def send_email(to, subject, body):
#     try:
#         msg = Message(
#             subject=subject,
#             recipients=[to],
#             body=body,
#             sender=("Free Fire Esports", MAIL_USERNAME or "no-reply@example.com")
#         )
#         mail.send(msg)
#     except Exception:
#         # fail silently for now
#         pass
# # ...existing code...
# # removed duplicate

# # # test
# # from flask_mail import Message
# # from extensions import mail

# # def send_email(to, subject, body):
# #     msg = Message(
# #         subject=subject,
# #         recipients=[to],
# #         body=body,
# #         sender=("Free Fire Esports", "syedasara2506@gmail.com")
# #     )
# #     mail.send(msg)
# # # test
# # @app.route("/test-email")
# # def test_email():
# #     send_email(
# #         to="yourgmail@gmail.com",
# #         subject="SMTP Working",
# #         body="Your Free Fire Esports platform email system works."
# #     )
# #     return "Email sent"
