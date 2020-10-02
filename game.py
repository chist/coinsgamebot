from bot import bot
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
   
    def run_out_of_time(self):
        self.out_of_time = True

    def receive_msg(self, text, tg_message=None):
        if tg_message is not None:
            bot.reply_to(tg_message, text)
        else:
            bot.send_message(self.chat_id, text)


class Game:
    default_balance = 20
    field_len = 5
    turn_duration = 30.0
    delay = 1.0
    timer = None
    
    def __init__(self, player_a, player_b):
        self.players = [player_a, player_b]
        for player in self.players:
            player.balance = Game.default_balance
            player.game = self
        self.position = Game.field_len // 2
        self.declare_turn()

    def get_player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                return player

    def get_position_str(self, player_id):
        if player_id == self.players[1].id:
            pos = self.position
        else:
            pos = Game.field_len - self.position - 1 
        
        s = ["⚪️\n"] * Game.field_len
        s[pos] = "🔴\n"
        return "".join(s)

    def get_opponent_str(self, player_id):
        for player in self.players:
            if player.id != player_id:
                s = player.name + f" [💰{player.balance}]\n"
                return s

    def get_player_str(self, player_id):
        for player in self.players:
            if player.id == player_id:
                s = f"You [💰{player.balance}]\n"
                return s

    def get_status_str(self, player):
        s = self.get_opponent_str(player.id)
        s += self.get_position_str(player.id)
        s += self.get_player_str(player.id)
        return s

    def send_status(self):
        for player in self.players:
            player.stake = None
            s = self.get_status_str(player)
            player.receive_msg(s)

    def check_time(self):
        """ Check if the game must be finished because of time limit """

        text_winner = "You opponent is out of time. You won."
        text_loser = "You're out of time! You lost."
        text_draw = "You're both out of time. It's a draw."
        if self.players[0].out_of_time and not self.players[1].out_of_time:
            self.players[0].receive_msg(text_loser)
            self.players[1].receive_msg(text_winner)
        elif not self.players[0].out_of_time and self.players[1].out_of_time:
            self.players[0].receive_msg(text_winner)
            self.players[1].receive_msg(text_loser)
        elif self.players[0].out_of_time and self.players[1].out_of_time:
            self.players[0].receive_msg(text_draw)
            self.players[1].receive_msg(text_draw)
        else:
            return
        self.finish_game()

    def declare_turn(self):
        for player in self.players:
            player.stake = None
            s = self.get_status_str(player)
            s += "\nLet's make a move!"
            s += f"\nYou have {int(Game.turn_duration)} seconds."
            player.receive_msg(s)
            player.timer = Timer(Game.turn_duration, player.run_out_of_time)
            player.timer.start()
        time = Game.turn_duration + Game.delay
        self.timer = Timer(time, self.check_time)
        self.timer.start()

    def accept_stake(self, stake, player_id, tg_message):
        player = self.get_player(player_id)

        if player.stake is not None:
            player.receive_msg("Your stake cannot be changed!")
            return

        if stake < 0:
            player.receive_msg("Stake must be non-negative!")
        elif player.balance < stake:
            text = f"Not enough money! You have 💰{player.balance}."
            player.receive_msg(text, tg_message=tg_message)
        else:
            player.timer.cancel()
            player.stake = stake
            text = "Your stake is accepted."
            player.receive_msg(text, tg_message=tg_message)

        # finish this phase
        if self.players[0].stake is not None and \
                self.players[1].stake is not None:
            self.timer.cancel()
            self.process_move()

    def process_move(self):
        if self.players[0].stake < self.players[1].stake:
            self.position -= 1
        elif self.players[0].stake > self.players[1].stake:
            self.position += 1

        for player in self.players:
            player.balance -= player.stake
            player.stake = None
       
        if self.position == 0:
            self.send_status()
            self.players[0].receive_msg("You lost!")
            self.players[1].receive_msg("You won!")
            self.finish_game()
        if self.position == Game.field_len - 1:
            self.send_status()
            self.players[0].receive_msg("You won!")
            self.players[1].receive_msg("You lost!")
            self.finish_game()
        elif self.players[0].balance == 0 and \
                self.players[1].balance >= self.position:
            self.send_status()
            self.players[0].receive_msg("You're out of money! You lost!")
            self.players[1].receive_msg("You won!" +
                    " Your opponent spent all the money.")
            self.finish_game()
        elif self.players[1].balance == 0 and \
                self.players[0].balance >= Game.field_len - self.position - 1:
            self.send_status()
            self.players[1].receive_msg("You're out of money! You lost!")
            self.players[0].receive_msg("You won!" +
                    " Your opponent spent all the money.")
            self.finish_game()
        elif self.players[0].balance < Game.field_len - self.position - 1 and \
                self.players[1].balance < self.position:
            self.send_status()
            msg = "It's a draw. No one has enough money to win."
            self.players[0].receive_msg(msg)
            self.players[1].receive_msg(msg)
            self.finish_game()
        else:
            self.declare_turn()

    def surrender(self, player_id):
        for player in self.players:
            player.game = None
            if player.id != player_id:
                player.receive_msg("Opponent left.")

    def finish_game(self):
        for player in self.players:
            if player.timer is not None:
                player.timer.cancel()
                player.timer = None
            player.game = None
            player.balance = None
            player.out_of_time = False
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

