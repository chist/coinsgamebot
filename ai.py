from player import Player
from decision_helper import Decision_helper
import random
import time


class PlayerAI(Player):
    def __init__(self, player_id, player_name, chat_id,
            cheat_central=0.25, cheat_defeat=0.4):
        super().__init__(player_id, player_name, chat_id)
        self.cheat_central, self.cheat_defeat = cheat_central, cheat_defeat
        random.seed()

    def get_opponent(self):
        for player in self.game.players:
            if player.id != self.id:
                return player

    def make_decision(self):
        """ choose stake value """

        position = self.game.position
        field_len = self.game.field_len
        default_balance = self.game.default_balance
        opponent = self.get_opponent()

        rand_val = random.uniform(0, 1)
        
        # possible cheating on the central cell
        try:
            if position == field_len // 2 and self.balance == opponent.balance \
                    and rand_val < self.cheat_central:
                if rand_val < self.cheat_central * 0.625:
                    d = field_len // 2
                else:
                    d = field_len // 2 - 1

                while opponent.stake is None and self.game is not None:
                    if opponent.game is None:
                        return 0
                    time.sleep(0.2)

                if opponent.stake <= self.game.default_balnce // 2 + 2:
                    stake = min(default_balance - d, opponent.stake + d)
                    return stake
        except:
            pass

        # make a balanced decision
        try:
            decision_helper = Decision_helper(field_len, default_balance)
            bal_a = opponent.balance
            bal_b = self.balance
            stake = decision_helper.decide(position, bal_a, bal_b)
        except:
            if self.balance is not None:
                stake = random.randint(0, self.balance)
            else:
                return 0

        # possible cheating before potential defeat
        try:
            if position == field_len - 2 and self.balance >= opponent.balance \
                    and rand_val < self.cheat_defeat:
                while opponent.stake is None and self.game is not None:
                    if opponent.game is None:
                        return 0
                    time.sleep(0.2)
                if opponent.stake > stake:
                    stake = random.randint(opponent.stake, 
                            min(self.balance, opponent.balance))
        except:
            pass

        return stake

    def check_players_order(self):
        """ Check that AI is the second player in a player list.
            It is needed to make correct decisions with Decision_helper. """
        assert self.id == self.game.players[1].id

    def start_turn_phase(self, time, msg_text):
        try:
            self.check_players_order()
            stake = self.make_decision()
            self.game.accept_stake(stake, self.id) 
        except Exception as e:
            if self.game is not None:
                print(f"Error in start_turn_phase(). {e}")


    def receive_msg(self, text, tg_message=None, keyboard=False):
        return
