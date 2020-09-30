import telebot
import config


class Bot:
    """ Singleton class to create bot object """

    __instance = None

    def get_instance():
        if Bot.__instance is None:
            Bot()
            return Bot.__instance

    def __init__(self, proxy=False):
        if Bot.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            telebot.apihelper.proxy = config.proxy_settings
            Bot.__instance = telebot.TeleBot(config.telegram_token)


bot = Bot.get_instance()
