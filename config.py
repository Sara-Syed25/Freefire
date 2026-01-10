# import os

# BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# class Config:
#     SECRET_KEY = "super-secret-key"
#     SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

# import os

# BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
# SQLALCHEMY_TRACK_MODIFICATIONS = False

# import os
# from dotenv import load_dotenv

# load_dotenv()

# MAIL_SERVER = os.getenv("MAIL_SERVER")
# MAIL_PORT = int(os.getenv("MAIL_PORT"))
# MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "True"
# MAIL_USERNAME = os.getenv("MAIL_USERNAME")
# MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "dev-secret-key"

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# JWT
JWT_SECRET_KEY = "jwt-secret-key"

# MAIL
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
