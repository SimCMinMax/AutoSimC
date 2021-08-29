"""
Internationalization functionality for AutoSimC.
"""
import gettext
import locale
import logging

from settings import settings
try:
    from settings_local import settings
except ImportError:
    pass


gettext.install('AutoSimC')
translator = gettext.translation('AutoSimC', fallback=True)

class TranslatedText(str):
    """Represents a translatable text string, while also keeping a reference to the original (English) string"""

    def __new__(cls, message, translate=True):
        if translate:
            return super(TranslatedText, cls).__new__(cls, translator.gettext(message))
        else:
            return super(TranslatedText, cls).__new__(cls, message)

    def __init__(self, message, translate=True):
        self.original_message = message

    def format(self, *args, **kwargs):
        s = TranslatedText(str.format(self, *args, **kwargs), translate=False)
        s.original_message = str.format(self.original_message, *args, **kwargs)
        return s


_ = TranslatedText


def install_translation():
    # Based on: (1) https://docs.python.org/3/library/gettext.html
    # (2) https://inventwithpython.com/blog/2014/12/20/translate-your-python-3-program-with-the-gettext-module/
    # Also see Readme.md#Localization for more info
    if settings.localization_language == "auto":
        # get the default locale using the locale module
        default_lang, _default_enc = locale.getdefaultlocale()
    else:
        default_lang = settings.localization_language
    try:
        if default_lang is not None:
            default_lang = [default_lang]
        lang = gettext.translation('AutoSimC', localedir='locale', languages=default_lang)
        lang.install()
        global translator
        translator = lang
    except FileNotFoundError:
        logging.debug("No translation for {} available.".format(default_lang))


install_translation()


class UntranslatedFileHandler(logging.FileHandler):
    """File Handler which logs messages untranslated"""

    def __init__(self, *args, **kwargs):
        kwargs['encoding'] = 'utf-8'
        super().__init__(*args, **kwargs)
        self.setFormatter(logging.Formatter("%(asctime)-15s %(levelname)s %(message)s"))

    def emit(self, record):
        if isinstance(record.msg, TranslatedText):
            orig_msg = record.msg
            try:
                record.msg = record.msg.original_message
                logging.FileHandler.emit(self, record)
            finally:
                record.msg = orig_msg
        else:
            logging.FileHandler.emit(self, record)
