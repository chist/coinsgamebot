from bot import bot, markup
from threading import Timer
from pymongo import MongoClient
from config import mongo_path


class Player:
    # database client
    client = MongoClient(mongo_path)

    default_rating = 1200

    def __init__(self, player_id, player_name, chat_id):
        """ initialize new player instance """

        # find player info in a database
        with Player.client as client:
            db = client.game_db
            user = db.players.find_one({"id": player_id})
            if user is None:
                # add user to database
                user = {"id": player_id,
                        "name": player_name,
                        "chat_id": chat_id,
                        "games_num": 0,
                        "rating": Player.default_rating}
                db.players.insert(user)
        
        self.id = user["id"]
        self.name = user["name"]
        self.chat_id = user["chat_id"]
        self.rating = user["rating"]
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
        """ send message back to user """

        # decide if custom keyboard is needed
        reply_markup = markup if (keyboard and self.game is None) else None

        if tg_message is not None:
            bot.reply_to(tg_message, text, reply_markup=reply_markup)
        else:
            bot.send_message(self.chat_id, text, reply_markup=reply_markup)

    def update_info(self):
        """ save info updates to database  """

        with Player.client as client:
            db = client.game_db
            user = db.players.find_one({"id": self.id})
            db.players.update({"_id": user["_id"]}, {"$inc": {"games_num": 1},
                "$set": {"rating": self.rating}}) 

    def go_offline(self):
        """ finish the game """

        # update player's info
        self.update_info()

        # reset game variables
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None
        self.game = None
        self.balance = None
        self.out_of_time = False

    def quit_after_error(self):
        self.receive_msg("Sorry, unexpected error has occured.", keyboard=True)
        self.go_offline()

