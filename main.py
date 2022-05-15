
from flask import abort, Response
import json
from flask import send_file
import socket
import traceback
import base64
import azure.cognitiveservices.speech as speechsdk
from flask_sqlalchemy import SQLAlchemy
from models import NameSpeech
from config import *
from sqlalchemy.sql import func
from sqlalchemy import or_
import logging
from src.phonetics import get_phonetic

logging.basicConfig(level=logging.INFO,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
audio_filePath = '/home/site/wwwroot/' if platform.system() != 'Windows' else 'D:/Sujit/hackathon/'
app.config['UPLOAD_FOLDER'] = audio_filePath
default_port = 8000
azure_host = "https://checkops.azurewebsites.net"

logging.info(audio_filePath)
logging.info(socket.gethostname())

""
"""Rest api for health check"""
""


@app.route('/ping')
def healthCheck():
    return "Speech api is running"

""
"""Function to create encoded audio path"""
""


def audio_path(file_name):
    full_path = audio_filePath+file_name

    sample_string_bytes = full_path.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    get_host_port = "http://"+socket.gethostname() + ":" + \
        str(default_port) if platform.system() == 'Windows' else azure_host

    return get_host_port+"/download/audio?q="+base64_string

""
"""Rest api to create/update default speech for user. If user exist, it will update all other details"""
""


@app.route('/speech/create', methods=['POST'])
def default_speech_save_update():  # sid, text, lang='en-US', gender='M'
    # Add validation
    logging.info('Add/Update api call...')
    content = request.get_json()
    sid = content['sid']
    f_name = content['firstName']
    l_name = content['lastName']
    s_name = content['shortName']
    logging.info(sid)
    text = content['text']
    iso_country = content['iso_country']
    iso_country = "US" if not content['iso_country'] else content['iso_country']
    lang = 'en' if not content['lang'] else content['lang']
    gender = 'M' if content['gender'] is None else content['gender']
    speech_config = speechsdk.SpeechConfig(
        subscription=subscription_key, region=default_region)
    default_voice_M = 'JasonNeural'

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


    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    callback = {"result": '', "callback_url": ''}
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        logging.info("Speech synthesized for text [{}]".format(text))
        phonetic_txt=get_phonetic(text)

        data_insert = NameSpeech(
            userID=sid,
            firstName=f_name,
            lastName=l_name,
            shortName=s_name,
            voicePath=audio_path(file_name),
            created=func.now(),
            custVoicePath='',
            phonetic=phonetic_txt,
        )
        record = NameSpeech.query.filter_by(user_id=sid).first()
        if not record:
            db.session.add(data_insert)
            db.session.commit()
            callback = {"result": 'success', "callback_url": audio_path(
                file_name), "sid": sid, "firstName": f_name, "lastName": l_name, "shortName": s_name, "custVoicePath": '',"phonetic":phonetic_txt}
            logging.info('Saved to DB')
        else:
            #User opting out custom speech and switching to default. provision to update other data. Refer update api for updating custom audio
            setattr(record, 'first_name', f_name)
            setattr(record, 'last_name', l_name)
            setattr(record, 'short_name', s_name)
            setattr(record, 'voice_path', audio_path(file_name))
            setattr(record, 'phonetic', phonetic_txt)
            db.session.commit()
            callback = {"result": 'success', "callback_url": audio_path(file_name), "sid": sid, "firstName": f_name,
                        "lastName": l_name, "shortName": s_name, "custVoicePath": '',"phonetic":phonetic_txt}
            logging.info('Updated to DB')
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:

        cancellation_details = speech_synthesis_result.cancellation_details
        callback = {"result": cancellation_details.error_details,
                    "callback_url": ''
                    }

        logging.info("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                logging.info("Error details: {}".format(
                    cancellation_details.error_details))
                logging.info("Did you set the speech resource key and region values?")

    logging.info("Callback URL: " + audio_callback_path)
    json_summary = jsonify(callback)
    response = make_response(json_summary, 201)
    return response

""
"""Rest api to update recorded speech for user. If File is not passed, the custom speech will be set to empty"""
""


@app.route('/speech/update', methods=['PUT'])
def record_speech():
    # Add validation

    sid = request.args.get('sid')
    logging.info("PrimaryKey: " +sid)

    record = NameSpeech.query.filter_by(user_id=sid).first()
    if not record:
        error_message = json.dumps({'error': f"Sid {sid} not found"})
        abort(Response(error_message, 201))
    logging.info(record.user_id)
    # check if the file has been uploaded
    if request.files.get('File', None):

        fileitem = request.files['File']

        # strip the leading path from the file name
        custom_path = fileitem.filename
        fileitem.save(audio_filePath+custom_path)
        print("Got the file saved: " + custom_path)
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

""
"""Rest api to search all users"""
""


@app.route("/search/profiles", methods=["GET"])
def view_all_profiles():
    if request.method == "GET":
        items = NameSpeech.query.all()
        resp = jsonify([item.serialize for item in items])
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp
    else:
        return {"message": "failure"}

""
"""Rest api to search user by SID or First/preferred name"""
""


@app.route("/search/profiles/<text>", methods=["GET"])
def search_profile(text):

    if request.method == "GET":
        try:
            search = "%{}%".format(text)
            items = db.session.query(NameSpeech).filter(
                or_(NameSpeech.first_name.like(search), NameSpeech.user_id.like(search)))
            resp = jsonify([item.serialize for item in items])
            resp.headers.add("Access-Control-Allow-Origin", "*")
            return resp
        except:
            traceback.logging.info_exc()
            resp = jsonify({"error": f"Item {text} not found"})
            resp.headers.add("Access-Control-Allow-Origin", "*")
            return resp
    else:
        return {"message": "Request method not implemented"}

"""Rest api to download audio file to client"""


@app.route("/download/audio", methods=["GET"])
def download_audio():
    logging.info("File Path-> "+request.args.get('q'))
    encoded_b64 = request.args.get('q')
    base64_bytes = encoded_b64.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    path = sample_string_bytes.decode("ascii")
    logging.info("Decoded Path-> " + path)
    return send_file(path, as_attachment=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.info('Starting speech api service..')

    if platform.system() != 'Windows':
        logging.info('Starting speech api service..on azure')
        app.run()
    else:
        logging.info('Starting speech api service..on local')
        app.run(host="0.0.0.0", port=default_port, debug=True)
