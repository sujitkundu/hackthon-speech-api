# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import azure.cognitiveservices.speech as speechsdk
from src.phonetics import *
from flask import *

subscription_key = 'c8e3d272c8a14b4a9b59c3fe18257c89'
default_region = 'eastus'
audio_filePath = 'C:/Users/Aditya Mangla/Desktop/'
app = Flask(__name__)


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


@app.route('/speech/default', methods=['POST'])
def default_speech():  # sid, text, lang='en-US', gender='M'
    # Add validation
    content = request.json
    sid = content['sid']
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
    audio_callback_path = audio_filePath+sid+"-def-file.wav"
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
    phonetic = get_phonetic(text)
    callback = {"result": '', "callback_url": '', "phonetic": phonetic}
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
        callback = {"result": 'success', "callback_url": audio_callback_path}
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
    response = make_response(json_summary, 200)
    return response


@app.route('/speech/voice', methods=['POST'])
def record_speech(sid, text, audio_file_path):
    # Add validation
    content = request.get_json(silent=True)
    sid = content['sid']
    print(sid)
    text = content['text']
    audio_file_path = request.values.get('audio_file_path')

    # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    audio_callback_path = audio_file_path  # audio_filePath + sid + "-def-file.wav";

    callback = {"callback_url": audio_callback_path}

    json_summary = jsonify(callback)
    response = make_response(json_summary, 200)
    return response


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('Starting speech api service..')
    app.run(host="0.0.0.0", port=8080, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
