import unittest

from main import *
from src.phonetics import *


class SpeechAPITest(unittest.TestCase):

    def test_default_speech(self):

        self.assertEqual("12345", "12345")

    # def test_get_phonetic(self):
    #     phonetic = get_phonetic("awanika")
    #     self.assertEqual("aditya*", phonetic)
