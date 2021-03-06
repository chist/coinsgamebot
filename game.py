from threading import Timer
from elo import rate_1vs1


class Game:
    default_balance = 20
    field_len = 5
    turn_duration = 20.0
    delay = 1.0
    timer = None
    
    def __init__(self, player_a, player_b):
        self.players = [player_a, player_b]
        for player in self.players:
            player.balance = Game.default_balance
            player.game = self
            player.searching = False
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
            self.players[0].receive_msg(text_loser, keyboard=True)
            self.players[1].receive_msg(text_winner, keyboard=True)
            self.finish_game(winner_idx=1)
        elif not self.players[0].out_of_time and self.players[1].out_of_time:
            self.players[0].receive_msg(text_winner, keyboard=True)
            self.players[1].receive_msg(text_loser, keyboard=True)
            self.finish_game(winner_idx=0)
        elif self.players[0].out_of_time and self.players[1].out_of_time:
            self.players[0].receive_msg(text_draw, keyboard=True)
            self.players[1].receive_msg(text_draw, keyboard=True)
            self.finish_game(winner_idx=None)

    def declare_turn(self):
        for player in self.players:
            player.stake = None
            s = self.get_status_str(player)
            s += "\nLet's make a move!"
            s += f"\nYou have {int(Game.turn_duration)} seconds."
            player.start_turn_phase(time=Game.turn_duration, msg_text=s)
        time = Game.turn_duration + Game.delay
        if self.timer is not None:
            self.timer.cancel()
        self.timer = Timer(time, self.check_time)
        self.timer.start()

    def accept_stake(self, stake, player_id, tg_message=None):
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
            if player.timer is not None:
                player.timer.cancel()
            player.stake = stake
            text = "Your stake is accepted."
            player.receive_msg(text, tg_message=tg_message)

        # finish this phase
        if self.players[0].stake is not None and \
                self.players[1].stake is not None:
            if self.timer is not None:
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
            self.players[0].receive_msg("You lost!", keyboard=True)
            self.players[1].receive_msg("You won!", keyboard=True)
            self.finish_game(winner_idx=1)
        elif self.position == Game.field_len - 1:
            self.send_status()
            self.players[0].receive_msg("You won!", keyboard=True)
            self.players[1].receive_msg("You lost!", keyboard=True)
            self.finish_game(winner_idx=0)
        elif self.players[0].balance == 0 and \
                self.players[1].balance >= self.position:
            self.send_status()
            self.players[0].receive_msg("You're out of money! You lost!",
                    keyboard=True)
            self.players[1].receive_msg("You won!" +
                    " Your opponent spent all the money.", keyboard=True)
            self.finish_game(winner_idx=1)
        elif self.players[1].balance == 0 and \
                self.players[0].balance >= Game.field_len - self.position - 1:
            self.send_status()
            self.players[1].receive_msg("You're out of money! You lost!",
                    keyboard=True)
            self.players[0].receive_msg("You won!" +
                    " Your opponent spent all the money.", keyboard=True)
            self.finish_game(winner_idx=0)
        elif self.players[0].balance < Game.field_len - self.position - 1 and \
                self.players[1].balance < self.position:
            self.send_status()
            msg = "It's a draw. No one has enough money to win."
            self.players[0].receive_msg(msg, keyboard=True)
            self.players[1].receive_msg(msg, keyboard=True)
            self.finish_game(winner_idx=None)
        else:
            self.declare_turn()

    def surrender(self, player_id):
        for player in self.players:
            player.game = None
            if player.id != player_id:
                player.receive_msg("Opponent left.", keyboard=True)
        winner_idx = 1 if player_id == self.players[0].id else 0
        self.finish_game(winner_idx=winner_idx, rating_msg=False)
    
    def update_ratings(self, winner_idx=None):
        """ update player ratings
        
            winner_idx is 0,    if self.players[0] has won
                          1,    if self.players[1] has won
                          None, otherwise
        """
  
        if winner_idx == 0:
            rtgs = rate_1vs1(self.players[0].rating, self.players[1].rating)
            self.players[0].rating_up = True
            self.players[1].rating_up = False
            self.players[0].rating = rtgs[0]
            self.players[1].rating = rtgs[1]
        elif winner_idx == 1:
            rtgs = rate_1vs1(self.players[1].rating, self.players[0].rating)
            self.players[0].rating_up = False
            self.players[1].rating_up = True
            self.players[1].rating = rtgs[0]
            self.players[0].rating = rtgs[1]
        elif winner_idx is None:
            rtgs = rate_1vs1(self.players[0].rating, self.players[1].rating,
                    drawn=True)
            if self.players[0].rating > self.players[1].rating:
                self.players[0].rating_up = False
                self.players[1].rating_up = True
            elif self.players[0].rating < self.players[1].rating:
                self.players[0].rating_up = True
                self.players[1].rating_up = False
            else:
                self.players[0].rating_up = True
                self.players[1].rating_up = True
            self.players[0].rating = rtgs[0]
            self.players[1].rating = rtgs[1]

    def finish_game(self, winner_idx=None, rating_msg=True):
        self.update_ratings(winner_idx=winner_idx)
        for player in self.players:
            rating = int(round(player.rating))
            if rating_msg:
                pic = "📈" if player.rating_up else "📉"
                player.receive_msg(f"Your rating is updated: {pic}{rating}.",
                        keyboard=True)
            player.go_offline()
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

