# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import base64

import azure.cognitiveservices.speech as speechsdk


import pandas
from flask_sqlalchemy import SQLAlchemy
from models import NameSpeech
from config import *

from sqlalchemy.ext.declarative import declarative_base

import datetime
from sqlalchemy.sql import func
from sqlalchemy import or_
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
import traceback
import socket
from flask import send_file
import os

import json
from flask import abort, Response

#DB_URL="host=20.127.242.100 port=5433 dbname=yugabyte user=yugabyte password=Hackathon22!"
#insert_sql= "INSERT INTO name_pronunciation_details (user_id, first_name, last_name, short_name,voice_path,created_timestamp) VALUES (%s, %s, %s, %s,%s,CURRENT_TIMESTAMP)";
#migrate = Migrate(app, db)
from sqlalchemy import create_engine
from sqlalchemy import MetaData
#engine_nf = create_engine('postgresql://yugabyte:Hackathon22!@20.127.242.100:5433/yugabyte')
#sql_read = lambda sql: pd.read_sql(sql, engine_nf)
#sql_execute = lambda sql: pd.io.sql.execute(sql, engine_nf)

#Base.metadata.create_all(engine_nf)

app.config['UPLOAD_FOLDER'] = audio_filePath

def audio_path(file_name):
    full_path= audio_filePath+file_name

    sample_string_bytes = full_path.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return "http://"+socket.gethostname()+":8080/download/audio?q="+base64_string;

@app.route('/speech/create',methods=['POST'])
def default_speech():#sid, text, lang='en-US', gender='M'
    #Add validation
    content= request.get_json()
    sid = content['sid']
    f_name = content['firstName']
    l_name = content['lastName']
    s_name = content['shortName']
    print(sid)
    text = content['text']
    iso_country = content['iso_country']
    iso_country = "US" if not content['iso_country'] else content['iso_country']
    lang = 'en' if not content['lang'] else content['lang']
    gender = 'M' if content['gender'] is None else content['gender']
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=default_region)
    default_voice_M = 'JasonNeural'

    #audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    file_name = sid+"-def-file.wav";
    audio_callback_path=audio_filePath+file_name;
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

        data_insert = NameSpeech(
            userID=sid,
            firstName=f_name,
            lastName=l_name,
            shortName=s_name,
            voicePath=audio_path(file_name),
            created=func.now(),
            custVoicePath='',
        )

        db.session.add(data_insert)
        db.session.commit()
        callback = {"result": 'success', "callback_url": audio_path(file_name), "sid":sid, "firstName": f_name, "lastName": l_name, "shortName":s_name, "custVoicePath":''}
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
    response = make_response(json_summary,201)
    return response

@app.route('/speech/update',methods=['PUT'])
def record_speech():
    # Add validation

    sid = request.args.get('sid')
    print(sid)

    fileitem = request.files['File']
    custom_path = fileitem.filename
    # check if the file has been uploaded
    if fileitem.filename:
        # strip the leading path from the file name
        fileitem.save(custom_path)

    record = NameSpeech.query.filter_by(user_id=sid).first()

    if not record:
        error_message = json.dumps({'error': f"Sid {sid} not found"})
        abort(Response(error_message, 201))

    print(record.user_id)

    #record.custVoicePath = audio_path(custom_path)
    setattr(record, 'custom_voice_path', audio_path(custom_path))

    db.session.commit()

    callback = {"result": 'success', "callback_url": record.voice_path, "sid": record.user_id, "firstName": record.first_name,
                "lastName": record.last_name, "shortName": record.short_name, "custVoicePath": audio_path(custom_path)}

    json_summary = jsonify(callback)
    response = make_response(json_summary, 201)
    return response


@app.route("/search/profiles", methods=["GET"])
def view_all_profiles():
    if request.method == "GET":
        items = NameSpeech.query.all()
        return jsonify([item.serialize for item in items])
    else:
        return {"message": "failure"}


@app.route("/search/profiles/<text>", methods=["GET"])
def search_profile(text):

    if request.method == "GET":
        try:
            #item = NameSpeech.query.filter_by(user_id=text).first_or_404()
            search = "%{}%".format(text)
            #items = NameSpeech.query.filter(NameSpeech.user_id.ilike('%' + text + '%')).all()

            # '%' attention to spaces
            #query_sql = """SELECT * FROM table WHERE user_id LIKE '%' :text '%' or first_name LIKE '%' :text '%' """
            # db is sqlalchemy session object
            #items = db.session.execute(text(query_sql), {"text": text}).fetchall()
            items = db.session.query(NameSpeech).filter(or_(NameSpeech.first_name.like(search), NameSpeech.user_id.like(search)))
            return jsonify([item.serialize for item in items])
        except:
            traceback.print_exc()
            return jsonify({"error": f"Item {text} not found"})
    else:
        return {"message": "Request method not implemented"}


@app.route("/download/audio", methods=["GET"])
def download_audio():
    print("File Path-> "+request.args.get('q'))
    encoded_b64=request.args.get('q');
    base64_bytes = encoded_b64.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    path = sample_string_bytes.decode("ascii")
    print("Decode Path-> " + path)
    return send_file(path, as_attachment=True)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Starting speech api service..')
    if os.path.exists(audio_filePath):
        app.run(host="0.0.0.0", port=8080, debug=True)
    else:
        print("The audio file path "+audio_filePath +" does not exist. Change the config path or create the same structure.")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
