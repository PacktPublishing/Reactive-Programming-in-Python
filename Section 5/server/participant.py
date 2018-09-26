from collections import defaultdict

class Participant:
    def __init__(self, name):
        self.name = name
        self.shares_log = []
        self.balance_log = []

    def __repr__(self):
        return self.name

    def shares_add(self, symbol, amount):
        self.shares_log.append((symbol, amount))

    def shares_remove(self, symbol, amount):
        self.shares_log.append((symbol, -amount))

    def balance_add(self, amount):
        self.balance_log.append(amount)

    def balance_subtract(self, amount):
        self.balance_log.append(-amount)
