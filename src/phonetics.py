import eng_to_ipa as ipa
import pronouncing

def get_phonetic(text):
    # phonetic = ipa.convert(text)
    phonetic = pronouncing.phones_for_word(text)
    return phonetic
