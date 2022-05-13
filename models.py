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
    created_timestamp = db.Column("created_timestamp",DateTime(timezone=False), default=func.now())

    def __init__(self, userID, firstName,lastName,shortName,voicePath,created):
        self.user_id = userID
        self.first_name = firstName
        self.last_name = lastName
        self.short_name = shortName
        self.voice_path = voicePath
        self.created_timestamp = created

    def __repr__(self):
        return f"<Item {self.userID}>"

    @property
    def serialize(self):
        """
        Return item in serializeable format
        """
        return {"userID": self.userID, "firstName": self.firstName}