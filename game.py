from bot import bot


class Player:
    def __init__(self, player_id, player_name, chat_id):
        self.id = player_id
        self.name = player_name
        self.chat_id = chat_id
        self.game = None
        self.balance = None
    
    def receive_msg(self, text):
        bot.send_message(self.chat_id, text)


class Game:
    default_balance = 20

    def __init__(self, player_a, player_b):
        self.players = [player_a, player_b]
        for player in self.players:
            player.balance = Game.default_balance
            player.game = self
        self.is_active = True
        self.declare_turn()

    def declare_turn(self):
        for player in self.players:
            player.receive_msg("New game started!")

    def surrender(self, player_id):
        self.is_active = False
        for player in self.players:
            player.game = None
            if player.id != player_id:
                player.receive_msg("Opponent left.")
