import random


class Situation():
    def __init__(self, field_len, pos, bal_a, bal_b, situation_dict):
        self.field_len = field_len
        self.pos = pos
        self.bal_a, self.bal_b = bal_a, bal_b
        self.winner, self.stake = None, None
        self.sd = situation_dict
        self.make_table()

    def make_table(self):
        """ create table of possible winners depending on stake realizations """

        bal_a, bal_b = self.bal_a, self.bal_b
        self.table = []
        for idx_a in range(bal_a + 1):
            self.table.append([])
            for idx_b in range(bal_b + 1):
                self.table[idx_a].append(None)

        # process trivial cases
        if bal_a == bal_b == 0:
            self.guess_winner()
            return
        if self.pos == 0 or self.pos == self.field_len - 1:
            self.guess_winner()
            return

        # brute-force all stake combinations
        for a in range(bal_a + 1):
            for b in range(bal_b + 1):
                if a == b == 0:
                    continue

                # calculate new chip possition
                if a > b:
                    new_pos = self.pos + 1
                elif a < b:
                    new_pos = self.pos - 1
                else:
                    new_pos = self.pos
                new_a, new_b = bal_a - a, bal_b - b

                # guess winner for the new situation
                self.table[a][b] = self.sd[new_pos][new_a][new_b].winner

        # guess winner for the current situation
        self.guess_winner()

    def guess_winner(self):
        """ guess who is likely to win and suggest a stake for AI """

        # process trivial cases
        if self.pos == 0:
            self.winner = "B"
            return "B"
        elif self.pos == self.field_len - 1:
            self.winner = "A"
            return "A"
        elif self.bal_a == self.bal_b == 0:
            self.winner = None
            return None

        # brute-force AI's stakes
        max_b_count, max_none_count = 0, 0
        cols = []
        for idx_b in range(self.bal_b + 1):
            # count number of wins and draws for a fixed stake of AI
            b_count, none_count = 0, 0
            for idx_a in range(self.bal_a + 1):
                winner = self.table[idx_a][idx_b]
                if winner == "B":
                    b_count += 1
                elif winner == None:
                    none_count += 1
            
            # choose best stake options
            if max_b_count == 0 and b_count == 0:
                if none_count > max_none_count:
                    max_none_count = none_count
                    cols = [idx_b]
                elif none_count == max_none_count:
                    cols.append(idx_b)
            elif b_count > max_b_count:
                max_b_count = b_count
                cols = [idx_b]
            elif b_count == max_b_count:
                cols.append(idx_b)
        
        # select one of the best options
        stake = random.choice(cols) if len(cols) > 0 else 0
        self.stake = stake
        
        # guess who will win
        lst = [self.table[idx_a][stake] for idx_a in range(self.bal_a + 1)]
        winner = max(set(lst), key=lst.count)
        self.winner = winner


class Decision_helper():
    def __init__(self, field_len, bal):
        self.situation_dict = {}
        random.seed()
        self.make_decision_tree(field_len, bal)

    def make_decision_tree(self, field_len, bal):
        """ create hierarchy of game situations """

        # initialize corner cases
        for pos in range(field_len):
            self.situation_dict[pos] = {0: {}}
            for bal_a in range(bal + 1):
                self.situation_dict[pos][bal_a] = {}
                for bal_b in range(min(bal, 2 * bal - bal_a) + 1):
                    if pos == 0 or pos == field_len - 1:
                        self.situation_dict[pos][bal_a][bal_b] = \
                                Situation(field_len, pos, bal_a, bal_b,
                                        self.situation_dict)
                    else:
                        self.situation_dict[pos][bal_a][bal_b] = None
            self.situation_dict[pos][0][0] = Situation(field_len, pos, 0, 0,
                    self.situation_dict) 

        for bal_sum in range(0, 2 * bal + 1):
            for bal_a in range(min(bal, bal_sum) + 1):
                bal_b = bal_sum - bal_a
                if bal_b > bal:
                    continue
                for pos in range(1, field_len-1):
                    self.situation_dict[pos][bal_a][bal_b] = \
                            Situation(field_len, pos, bal_a, bal_b,
                                    self.situation_dict)

    def decide(self, pos, bal_a, bal_b):
        """ place a bet """
        return self.situation_dict[pos][bal_a][bal_b].stake

