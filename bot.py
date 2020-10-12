import telebot
from telebot import types
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
            Bot.__instance = telebot.TeleBot(config.telegram_token)


# create telegram bot instance
bot = Bot.get_instance()

# create custom keyboard for the game
markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
btn1 = types.KeyboardButton('/rules')
btn2 = types.KeyboardButton('/singleplayer')
btn3 = types.KeyboardButton('/multiplayer')
markup.add(btn1, btn2, btn3)
