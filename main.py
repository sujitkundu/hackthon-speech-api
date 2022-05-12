# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import azure.cognitiveservices.speech as speechsdk
from flask import g
#from flask import request,make_response,Flask,jsonify,appcontext_tearing_down,request_started
import psycopg2
import asyncio
#from sqlalchemy import create_engine
import pandas
from flask_sqlalchemy import SQLAlchemy
from models import NameSpeech
from config import *
from models import Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from sqlalchemy.sql import func

#DB_URL="host=20.127.242.100 port=5433 dbname=yugabyte user=yugabyte password=Hackathon22!"
#insert_sql= "INSERT INTO name_pronunciation_details (user_id, first_name, last_name, short_name,voice_path,created_timestamp) VALUES (%s, %s, %s, %s,%s,CURRENT_TIMESTAMP)";
#migrate = Migrate(app, db)
from sqlalchemy import create_engine
from sqlalchemy import MetaData
engine_nf = create_engine('postgresql://yugabyte:Hackathon22!@20.127.242.100:5433/yugabyte')
#sql_read = lambda sql: pd.read_sql(sql, engine_nf)
#sql_execute = lambda sql: pd.io.sql.execute(sql, engine_nf)

#Base.metadata.create_all(engine_nf)

@app.route('/speech/default',methods=['POST'])
def default_speech():#sid, text, lang='en-US', gender='M'
    #Add validation
    content= request.get_json(silent=True)
    sid = content['sid']
    print(sid)
    text = content['text']
    iso_country = content['iso_country']
    iso_country = "US" if not content['iso_country'] else content['iso_country']
    lang = 'en' if not content['lang'] else content['lang']
    gender = 'M' if content['gender'] is None else content['gender']
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=default_region)
    default_voice_M = 'JasonNeural'

    #audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    audio_callback_path=audio_filePath+sid+"-def-file.wav";
    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_callback_path)

    # The language of the voice that speaks.
    speaker = default_voice_M if gender=='M' else 'NancyNeural'
    speech_config.speech_synthesis_voice_name = lang+ "-" + iso_country + '-' + speaker

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Get text from the console and synthesize to the default speaker.
    #print("Enter some text that you want to speak >")
    #text = input(name)

    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    callback = {"result": '', "callback_url": ''}
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
        callback = {"result": 'success',"callback_url": audio_callback_path}
        data_insert = NameSpeech(
            userID=sid,
            firstName=text,
            lastName=text,
            shortName=text,
            voicePath=audio_callback_path,
            created=func.now(),
        )
        #Session = sessionmaker(bind=engine_nf)

        db.session.add(data_insert)
        db.session.commit()
        print('Saved to DB')
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:

        cancellation_details = speech_synthesis_result.cancellation_details
        callback = {"result": cancellation_details.error_details ,
                    "callback_url":''
                    }

        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

    print("Callback URL: "+ audio_callback_path)
    json_summary = jsonify(callback)
    response = make_response(json_summary,200)
    return response

@app.route('/speech/voice',methods=['POST'])
def record_speech(sid, text,audio_file_path):
    # Add validation
    content = request.get_json(silent=True)
    sid = content['sid']
    print(sid)
    text = content['text']
    audio_file_path=request.values.get('audio_file_path')

    # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    audio_callback_path = audio_file_path #audio_filePath + sid + "-def-file.wav";

    callback = {"callback_url": audio_callback_path}

    json_summary = jsonify(callback)
    response = make_response(json_summary, 200)
    return response


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Starting speech api service..')
    app.run(host="0.0.0.0", port=8080, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
