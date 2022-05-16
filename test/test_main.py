import json
import unittest
from unittest.mock import MagicMock

import validators
from alchemy_mock.mocking import UnifiedAlchemyMagicMock

import main
from main import app, audio_path


class test_main(unittest.TestCase):

    def setUp(self):
        global req_data
        self.test_app = app.test_client()
        filepath = 'request.json'
        with open(filepath, 'r') as f:
            req_data = json.loads(f.read())


    def tearDown(self):
        pass

    def testSpeechSearchProfiles(self):
        name = main.NameSpeech(userID=456, firstName="AAA", lastName="BBB", shortName="ABC", voicePath="", created="2022-05-14 10:08:01.38305 ", custVoicePath="", phonetic="ABC")
        main.NameSpeech = MagicMock(return_value=name)
        response = self.test_app.get('/search/profiles', content_type='application/json',
                                      data=json.dumps(req_data),
                                      follow_redirects=True)
        self.assertEqual(response.status, "200 OK")
        return response

    def testAudioPath(self):
        response = audio_path('sample.txt')
        valid = validators.url(response)
        self.assertFalse(valid)

    def testSpeechSearchSpecificProfile(self):
        main.db.session = UnifiedAlchemyMagicMock()

        name = main.NameSpeech(userID="123", firstName="AAA123", lastName="BBB", shortName="ABC", voicePath="",
                               created="2022-05-14 10:08:01.38305 ", custVoicePath="", phonetic="ABC")

        main.db.session.query(name).filter = MagicMock(side_effect=[{name}])
        main.jsonify = MagicMock(side_effect=[{"user_id" : "123", "first_name" : "AAA123", "last_name" : "BBB", "short_name": "ABC", "voice_path" : "","custom_voice_path" : "", "created_timestamp" : "2022-05-14 10:08:01.38305 ", "phonetic" : "ABC" }])
        response = self.test_app.get('/search/profiles/123', content_type='application/json',
                                                                          follow_redirects=True)
        self.assertRaises(Exception)


    def testSpeechUpdate(self):
        response = self.test_app.put('/speech/update', query_string= {'sid': '6789'}, content_type='application/json',
                                     data=json.dumps(req_data),
                                     follow_redirects=True)
        self.assertEqual(response.status, "201 CREATED")
        return response

