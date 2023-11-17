def reverse_dict(original_dict):
    switched_dict = {value: key for key, value in original_dict.items()}
    return switched_dict

ISO_TO_LANG = {
    'nb_NO': 'Norwegian',
    'es_ES': 'Spanish (European)',
    'en_US': 'English (American)',
    'en_GB': 'English (British)',
    'en_AU': 'English (Australian)',
    'es_US': 'Spanish (American)',
    'da_DK': 'Danish',
    'nl_NL': 'Dutch',
    'de_DE': 'German',
    'fr_FR': 'French',
    'it_IT': 'Italian',
    'is_IS': 'Icelandic',
    'pt_PT': 'Portuguese (European)',
    'pt_BR': 'Portuguese (Brazilian)',
    'ru_RU': 'Russian',
    'ru_RO': 'Romanian',
    'ja_JP': 'Japanese',
    'arb': 'Arabic',
    'sv_SE': 'Swedish',
}

LANG_TO_ISO = reverse_dict(ISO_TO_LANG)

ISO_TO_VOICE_ID = {
    'en_AU': 'Russell',
    'en_GB': 'Brian',
    'da_DK': 'Mads',
    'es_ES': 'Enrique',
    'en_US': 'Joey',
    'nl_NL': 'Ruben',
    'es_US': 'Lupe',
    'de_DE': 'Hans',
    'fr_FR': 'Mathieu',
    'it_IT': 'Giorgio',
    'is_IS': 'Karl',
    'pt_PT': 'Cristiano',
    'pt_BR': 'Ricardo',
    'ru_RU': 'Maxim',
    'ru_RO': 'Carmen',
    'ja_JP': 'Takumi',
    'arb': 'Zeina',
    'sv_SE': 'Astrid',
    'nb_NO': 'Liv',
}

