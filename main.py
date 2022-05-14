# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from flask import abort, Response
import json
import gunicorn
import os
from flask import send_file
import socket
import traceback
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


#DB_URL="host=20.127.242.100 port=5433 dbname=yugabyte user=yugabyte password=Hackathon22!"
#insert_sql= "INSERT INTO name_pronunciation_details (user_id, first_name, last_name, short_name,voice_path,created_timestamp) VALUES (%s, %s, %s, %s,%s,CURRENT_TIMESTAMP)";
#migrate = Migrate(app, db)
#engine_nf = create_engine('postgresql://yugabyte:Hackathon22!@20.127.242.100:5433/yugabyte')
#sql_read = lambda sql: pd.read_sql(sql, engine_nf)
#sql_execute = lambda sql: pd.io.sql.execute(sql, engine_nf)

# Base.metadata.create_all(engine_nf)

audio_filePath = '/home/site/wwwroot/' if platform.system() != 'Windows' else 'D:/Sujit/hackathon/'

app.config['UPLOAD_FOLDER'] = audio_filePath
default_port = 8000
azure_host = "https://checkops.azurewebsites.net"

print(audio_filePath)
print(socket.gethostname())


@app.route('/ping')
def index():
    return "Speech api is running"


def audio_path(file_name):
    full_path = audio_filePath+file_name

    sample_string_bytes = full_path.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    get_host_port = "http://"+socket.gethostname() + ":" + \
        str(default_port) if platform.system() == 'Windows' else azure_host

    return get_host_port+"/download/audio?q="+base64_string


@app.route('/speech/create', methods=['POST'])
def default_speech_save_update():  # sid, text, lang='en-US', gender='M'
    # Add validation
    print('Adding new...')
    content = request.get_json()
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
    speech_config = speechsdk.SpeechConfig(
        subscription=subscription_key, region=default_region)
    default_voice_M = 'JasonNeural'

    #audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    file_name = sid+"-def-file.wav"
    audio_callback_path = audio_filePath+file_name
    audio_config = speechsdk.audio.AudioOutputConfig(
        filename=audio_callback_path)

    # The language of the voice that speaks.
    speaker = default_voice_M if gender == 'M' else 'NancyNeural'
    speech_config.speech_synthesis_voice_name = lang + \
        "-" + iso_country + '-' + speaker

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config)

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
            phonetic='',
        )
        record = NameSpeech.query.filter_by(user_id=sid).first()
        if not record:
            db.session.add(data_insert)
            db.session.commit()
            callback = {"result": 'success', "callback_url": audio_path(
                file_name), "sid": sid, "firstName": f_name, "lastName": l_name, "shortName": s_name, "custVoicePath": '',"phonetic":''}
            print('Saved to DB')
        else:
            setattr(record, 'voice_path', audio_path(file_name))
            db.session.commit()
            callback = {"result": 'success', "callback_url": audio_path(file_name), "sid": sid, "firstName": f_name,
                        "lastName": l_name, "shortName": s_name, "custVoicePath": '',"phonetic":''}
            print('Updated to DB')
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:

        cancellation_details = speech_synthesis_result.cancellation_details
        callback = {"result": cancellation_details.error_details,
                    "callback_url": ''
                    }

        print("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(
                    cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

    print("Callback URL: " + audio_callback_path)
    json_summary = jsonify(callback)
    response = make_response(json_summary, 201)
    return response


@app.route('/speech/update', methods=['PUT'])
def record_speech():
    # Add validation

    sid = request.args.get('sid')
    print(sid)

    record = NameSpeech.query.filter_by(user_id=sid).first()
    if not record:
        error_message = json.dumps({'error': f"Sid {sid} not found"})
        abort(Response(error_message, 201))
    print(record.user_id)
    # check if the file has been uploaded
    if request.files.get('File', None):
        fileitem = request.files['File']
        # strip the leading path from the file name
        custom_path = fileitem.filename
        fileitem.save(custom_path)
        setattr(record, 'custom_voice_path', audio_path(custom_path))
        callback = {"result": 'success', "callback_url": record.voice_path, "sid": record.user_id,
                    "firstName": record.first_name,
                    "lastName": record.last_name, "shortName": record.short_name,
                    "custVoicePath": audio_path(custom_path),"phonetic":record.phonetic}
    else:
        # Reset custom voice to empty
        setattr(record, 'custom_voice_path', '')
        callback = {"result": 'success', "callback_url": record.voice_path, "sid": record.user_id,
                    "firstName": record.first_name,
                    "lastName": record.last_name, "shortName": record.short_name,
                    "custVoicePath": '',"phonetic":record.phonetic}

    db.session.commit()

    json_summary = jsonify(callback)
    response = make_response(json_summary, 201)
    return response


@app.route("/search/profiles", methods=["GET"])
def view_all_profiles():
    if request.method == "GET":
        items = NameSpeech.query.all()
        resp = jsonify([item.serialize for item in items])
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp
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
            items = db.session.query(NameSpeech).filter(
                or_(NameSpeech.first_name.like(search), NameSpeech.user_id.like(search)))
            # return jsonify([item.serialize for item in items])
            resp = jsonify([item.serialize for item in items])
            resp.headers.add("Access-Control-Allow-Origin", "*")
            return resp
        except:
            traceback.print_exc()
            resp = jsonify({"error": f"Item {text} not found"})
            resp.headers.add("Access-Control-Allow-Origin", "*")
            return resp
    else:
        return {"message": "Request method not implemented"}


@app.route("/download/audio", methods=["GET"])
def download_audio():
    print("File Path-> "+request.args.get('q'))
    encoded_b64 = request.args.get('q')
    base64_bytes = encoded_b64.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    path = sample_string_bytes.decode("ascii")
    print("Decode Path-> " + path)
    return send_file(path, as_attachment=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Starting speech api service..')
    if platform.system() != 'Windows':
        print('Starting speech api service..on azure')
        app.run()
    else:
        print('Starting speech api service..on local')
        app.run(host="0.0.0.0", port=default_port, debug=True)

    # if os.path.exists(audio_filePath):
    #     app.run(host="0.0.0.0", port=default_port, debug=True)
    # else:
    #     print("The audio file path "+audio_filePath +" does not exist. Change the config path or create the same structure.")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
