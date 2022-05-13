from flask import request, make_response, Flask, jsonify, appcontext_tearing_down, request_started
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

subscription_key = 'c8e3d272c8a14b4a9b59c3fe18257c89'
default_region = 'eastus'
audio_filePath = 'C:/USERS/Aditya Mangla/Desktop/'
app = Flask(__name__)
CORS(app)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://yugabyte:Hackathon22!@20.127.242.100:5433/yugabyte"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
