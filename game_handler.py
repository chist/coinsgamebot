from bot import bot
from queue import Queue
from game import Player, Game


class Game_handler:
    players = {}
    players_queue = Queue()

    @bot.message_handler(commands=["start"])
    def send_welcome(message):
        bot.reply_to(message, "Welcome!")

    @bot.message_handler(commands=["newgame"])
    def join_game(message):
        """ Attach player to a game """
        
        # get player info
        player_id = message.from_user.id
        player_name = message.from_user.first_name

        # find the player among known players 
        if player_id in Game_handler.players.keys():
            if Game_handler.players[player_id].game is not None:
                Game_handler.players[player_id].game.surrender(player_id)
            new_player = Game_handler.players[player_id]
        else:
            new_player = Player(player_id, player_name, message.chat.id)
            Game_handler.players[player_id] = new_player
        
        bot.reply_to(message, "Looking for an opponent...")
        Game_handler.players_queue.put(new_player)

        # match players if possible
        if Game_handler.players_queue.qsize() >= 2:
            player_a = Game_handler.players_queue.get()
            player_b = Game_handler.players_queue.get()
            if player_a.id != player_b.id:
                Game(player_a, player_b)
            else:
                Game_handler.players_queue.put(player_a)

    @bot.message_handler(func=lambda message: True)
    def make_stake(message):
        """ Accept user's stake """
        
        player_id = message.from_user.id
        player = Game_handler.players[player_id]
        
        if player.game is None:
            bot.reply_to(message, "I don't understand your message.")
            return

        stake = int(message.text)
        player.game.accept_stake(stake, player_id)
