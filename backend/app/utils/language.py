from dataclasses import dataclass

@dataclass
class VoiceId:
    name: str
    engine: str = 'standard'

def reverse_dict(original_dict):
    switched_dict = {value: key for key, value in original_dict.items()}
    return switched_dict

ISO_TO_LANG = {
    'en_US': 'English',
    'en_GB': 'English (British)',
    #'en_IE': 'English (Ireland)', *no standard voice
    'en_AU': 'English (Australian)',
    'ca_ES': 'Catalan',
    'cmn_CN': 'Chinese (Mandarin)',
    'es_US': 'Spanish (American)',
    'es_MX': 'Spanish (Mexican)',
    'es_ES': 'Spanish (European)',
    'da_DK': 'Danish',
    'nl_NL': 'Dutch',
    'de_DE': 'German',
    'fr_FR': 'French',
    'fr_CA': 'French (Canadian)',
    'hi_IN': 'Hindi',
    'it_IT': 'Italian',
    'is_IS': 'Icelandic',
    'nb_NO': 'Norwegian',
    'pl_PL': 'Polish',
    'pt_PT': 'Portuguese (European)',
    'pt_BR': 'Portuguese (Brazilian)',
    'ru_RU': 'Russian',
    'ru_RO': 'Romanian',
    'tr_TR': 'Turkish',
    'ja_JP': 'Japanese',
    'cy_GB': 'Welsh',
    'arb': 'Arabic',
    'sv_SE': 'Swedish',
}

LANG_TO_ISO = reverse_dict(ISO_TO_LANG)

ISO_TO_VOICE_ID = {
    'cmn_CN': VoiceId(name='Zhiyu'),
    'tr_TR': VoiceId(name='Filiz'),
    'cy_GB': VoiceId(name='Gwyneth'),
    'es_MX': VoiceId(name='Mia'),
    'pl_PL': VoiceId(name='Jacek'),
    'hi_IN': VoiceId(name='Aditi'),
    'fr_CA': VoiceId(name='Chantal'),
    'en_AU': VoiceId(name='Russell'),
    'en_GB': VoiceId(name='Brian'),
    'da_DK': VoiceId(name='Mads'),
    'es_ES': VoiceId(name='Sergio', engine='neural'),
    'ca_ES': VoiceId(name='Arlet', engine='neural'),
    'en_US': VoiceId(name='Joey'),
    'nl_NL': VoiceId(name='Ruben'),
    'es_US': VoiceId(name='Lupe'),
    'de_DE': VoiceId(name='Hans'),
    'fr_FR': VoiceId(name='Mathieu'),
    'it_IT': VoiceId(name='Giorgio'),
    'is_IS': VoiceId(name='Karl'),
    'pt_PT': VoiceId(name='Cristiano'),
    'pt_BR': VoiceId(name='Ricardo'),
    'ru_RU': VoiceId(name='Maxim'),
    'ru_RO': VoiceId(name='Carmen'),
    'ja_JP': VoiceId(name='Takumi'),
    'arb': VoiceId(name='Zeina'),
    'sv_SE': VoiceId(name='Astrid'),
    'nb_NO': VoiceId(name='Liv')
}

