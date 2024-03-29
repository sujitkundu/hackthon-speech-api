import platform

from flask import request,make_response,Flask,jsonify,appcontext_tearing_down,request_started

from flask_sqlalchemy import SQLAlchemy
import platform
from flask_cors import CORS

subscription_key = 'c8e3d272c8a14b4a9b59c3fe18257c89'
default_region = 'eastus'
audio_filePath = '/home/site/wwwroot/' if platform.system() != 'Windows' else 'D:/Sujit/hackathon/'
app= Flask(__name__)
CORS(app)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://yugabyte:Hackathon22!@20.127.242.100:5433/yugabyte"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'connect_timeout': 20
    }
}
db = SQLAlchemy(app)

