from sqlalchemy import Column, Integer, String, DateTime, TIMESTAMP, text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import datetime
from config import db
Base = declarative_base()

class NameSpeech(db.Model):
    """
    Defines the name_pronunciation_details model
    """

    __tablename__ = "name_pronunciation_details"

    user_id = db.Column("user_id",db.String, primary_key=True)
    first_name = db.Column("first_name",db.String)
    last_name = db.Column("last_name",db.String)
    short_name = db.Column("short_name",String)
    voice_path = db.Column("voice_path",String)
    custom_voice_path=  db.Column("custom_voice_path",String)
    created_timestamp = db.Column("created_timestamp",DateTime(timezone=False), default=func.now())
    phonetic = db.Column("phonetic", String)

    def __init__(self, userID, firstName,lastName,shortName,voicePath,created,custVoicePath,phonetic):
        self.user_id = userID
        self.first_name = firstName
        self.last_name = lastName
        self.short_name = shortName
        self.voice_path = voicePath
        self.created_timestamp = created
        self.custom_voice_path= custVoicePath
        self.phonetic = phonetic

    def __repr__(self):
        return {"sid": self.user_id, "firstName": self.first_name, "lastName": self.last_name,"shortName":self.short_name,"voicePath":self.voice_path,"custom_voice_path":self.custom_voice_path,"created_time":self.created_timestamp,"phonetic":self.phonetic}

    @property
    def serialize(self):
        """
        Return item in serializeable format
        """
        return {"sid": self.user_id, "firstName": self.first_name, "lastName": self.last_name,"shortName":self.short_name,"voicePath":self.voice_path,"custom_voice_path":self.custom_voice_path,"created_time":self.created_timestamp,"phonetic":self.phonetic}

