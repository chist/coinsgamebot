from bot import bot, markup
from collections import deque
from player import Player
from ai import PlayerAI
from game import Game
from threading import Timer
import pymongo
from config import mongo_path


class Game_handler:
    # database client
    client = pymongo.MongoClient(mongo_path)
    
    search_time = 60.0
    players = {}
    players_queue = deque()
    rules_link = "https://telegra.ph/Coins-game-rules-10-05"
    top_size = 10
    
    @bot.message_handler(commands=["top"])
    def get_top(message):
        users, text_reply = [], ""
        with Game_handler.client as client:
            db = client.game_db
            users = db.players.find().sort("rating", pymongo.DESCENDING)
        users = list(users[:Game_handler.top_size])
        max_name_len = max([len(user["name"]) for user in users])
        for idx, user in enumerate(users):
            rating = int(round(user["rating"]))
            name_str = user["name"]
            new_str = f"{idx + 1}. (⭐️{rating}) {name_str}\n"
            if user["id"] == message.from_user.id:
                new_str = "*" + new_str + "*"
            text_reply += new_str

        # decide if custom keyboard is needed
        player = Game_handler.find_player(message, new_game=False)
        reply_markup = markup if player.game is None else None
        
        bot.reply_to(message, text_reply, reply_markup=reply_markup,
                parse_mode="Markdown")

    @bot.message_handler(commands=["start", "rules"])
    def send_welcome(message):
        text_reply = "See the rules there:\n"
        text_reply += Game_handler.rules_link + "\n\n"
        text_reply += "Start a new game with /singleplayer or /multiplayer."
        
        # decide if custom keyboard is needed
        player = Game_handler.find_player(message, new_game=False)
        reply_markup = markup if player.game is None else None

        bot.reply_to(message, text_reply, reply_markup=reply_markup)
   
    def find_player(message, new_game=True):
        """ Find message sender among known players """
        
        # get player info
        player_id = message.from_user.id
        player_name = message.from_user.first_name
        
        # find the player among known players 
        if player_id in Game_handler.players.keys():
            if Game_handler.players[player_id].game is not None and new_game:
                Game_handler.players[player_id].game.surrender(player_id)
            player = Game_handler.players[player_id]
        else:
            player = Player(player_id, player_name, message.chat.id)
            Game_handler.players[player_id] = player

        return player

    @bot.message_handler(commands=["singleplayer"])
    def single_player(message):
        """ create game with bot """

        player_a = Game_handler.find_player(message)
        player_b = PlayerAI(player_id=0, player_name="AI", chat_id=None)
        Game_handler.start_game(player_a, player_b) 

    @bot.message_handler(commands=["multiplayer"])
    def multiplayer(message):
        """ Add player to the queue """
        
        new_player = Game_handler.find_player(message)
        bot.reply_to(message, "Looking for an opponent...")

        # reset timer
        if new_player.timer is not None:
            new_player.timer.cancel()
        new_player.timer = Timer(Game_handler.search_time,
                new_player.stop_searching)
        new_player.timer.start()
       
        # add player to the queue if needed
        new_player.searching = True
        if Game_handler.players_queue.count(new_player) == 0:
            Game_handler.players_queue.append(new_player)
        else:
            return

        # match players and start a game if possible
        Game_handler.match_players()

    @bot.message_handler(func=lambda message: True)
    def make_stake(message):
        """ Accept user's stake """
        
        player_id = message.from_user.id
        try:
            player = Game_handler.players[player_id]
        except Exception:
            player_id = message.from_user.id
            player_name = message.from_user.first_name
            player = Player(player_id, player_name, message.chat.id)
            Game_handler.players[player_id] = player

        if player.game is None:
            bot.reply_to(message, "I don't understand your message." +
                    " Start a new game with /singleplayer or /multiplayer.",
                    reply_markup=markup)
            return

        try:
            stake = int(message.text)
            player.game.accept_stake(stake, player_id, message)
        except Exception:
            bot.reply_to(message, "Stake value must be an integer number!")

    def match_players():
        if len(Game_handler.players_queue) >= 2:
            # check if players are still online
            player_a = Game_handler.players_queue.popleft()
            if not player_a.searching:
                return
            player_b = Game_handler.players_queue.popleft()
            if not player_b.searching or player_a.id == player_b.id:
                Game_handler.players_queue.appendleft(player_a)
                return

            # start game
            Game_handler.start_game(player_a, player_b)

    def start_game(player_a, player_b):
        """ create game instance """

        for player in [player_a, player_b]:
            if player.timer is not None:
                player.timer.cancel()
                player.timer = None

        try:
            Game(player_a, player_b)
        except Exception as e:
            print(f"Error during a game. {e}")
            for player in [player_a, player_b]:
                player.quit_after_error()

