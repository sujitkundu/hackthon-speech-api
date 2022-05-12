import eng_to_ipa as ipa


def get_phonetic(text):
    phonetic = ipa.convert(text)
    return phonetic
