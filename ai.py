from player import Player
import random


class PlayerAI(Player):
    def __init__(self, player_id, player_name, chat_id):
        super().__init__(player_id, player_name, chat_id)
        random.seed()
    
    def get_advantage(self):
        for player_idx, player in enumerate(self.game.players):
            if player.id != self.id:
                continue

            if player_idx == 0:
                return self.position - (Gself.game.field_len) // 2
            else:
                return (self.game.field_len // 2) - self.position

    def get_opponent(self):
        for player in self.game.players:
            if player.id != self.id:
                return player

    def make_decision(self):
        adv = self.game.get_advantage(self.id)
        if adv == self.game.field_len - self.game.field_len // 2 - 2 and \
                self.balance > self.get_opponent().balance:
            stake = self.balance
        else:
            stake = random.randint(0, self.balance // 2)
        return stake

    def start_turn_phase(self, time, msg_text):
        stake = self.make_decision()
        self.game.accept_stake(stake, self.id) 

    def receive_msg(self, text, tg_message=None):
        return
