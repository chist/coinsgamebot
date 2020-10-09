from bot import bot, markup
from threading import Timer


class Player:
    def __init__(self, player_id, player_name, chat_id):
        self.id = player_id
        self.name = player_name
        self.chat_id = chat_id
        self.game = None
        self.balance = None
        self.stake = None
        self.timer = None
        self.out_of_time = False
        self.searching = False

    def stop_searching(self):
        """ Stop searching for an opponent """
        self.searching = False
        self.receive_msg("No one is online :(", keyboard=True)

    def run_out_of_time(self):
        """ Turn is finished because of time limit """
        self.out_of_time = True

    def start_turn_phase(self, time, msg_text):
        self.receive_msg(msg_text)
        self.timer = Timer(time, self.run_out_of_time)
        self.timer.start()

    def receive_msg(self, text, tg_message=None, keyboard=False):
        if keyboard:
            bot.send_message(self.chat_id, text, reply_markup=markup)
            return

        if tg_message is not None:
            bot.reply_to(tg_message, text)
        else:
            bot.send_message(self.chat_id, text)

    def go_offline(self):
        """ reset game stats """
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None
        self.game = None
        self.balance = None
        self.out_of_time = False

    def quit_after_error(self):
        self.receive_msg("Sorry, unexpected error has occured.", keyboard=True)
        self.go_offline()

