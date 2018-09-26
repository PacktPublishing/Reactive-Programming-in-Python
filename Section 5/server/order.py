import datetime

from participant import Participant

class Order:
    SELL = 'sell'
    BUY = 'buy'

    @classmethod
    def from_list(cls, attrs):
        return cls(
            posted_by=Participant(attrs[0]),
            stock_symbol=attrs[1],
            direction=attrs[2],
            amount=int(attrs[3]),
            price=float(attrs[4]),
        )

    def __init__(self, posted_by, direction, stock_symbol, amount, price):
        self.timestamp = datetime.datetime.now()
        self.direction = direction
        self.stock_symbol = stock_symbol
        self.amount = amount
        self.price = price
        self.fulfilled = False
        self.fulfilled_by = None
        self.posted_by = posted_by

    def __repr__(self):
        return '{}: {} {} {} @ ${}'.format(self.posted_by, self.direction, self.stock_symbol, self.amount, self.price)

    def __lt__(self, other_order):
        return self.timestamp < other_order.timestamp

    def to_csv(self):
        return [
            self.posted_by,
            self.stock_symbol,
            self.direction,
            str(self.amount),
            str(self.price),
        ].join(',')

    def matches(self, other_order):
        return self.amount <= other_order.amount and self.price_matches(other_order.price) and self.direction != other_order.direction

    def price_matches(self, price):
        return True

    def fulfill(self, participant):
        self.fulfilled = True
        self.fulfilled_by = participant
        if self.direction == Order.BUY:
            participant.balance_subtract(self.price)
            participant.shares_add(self.stock_symbol, self.amount)
            self.posted_by.balance_add(self.price)
            self.posted_by.shares_subtract(self.stock_symbol, self.amount)
        elif self.direction == Order.SELL:
            participant.balance_add(self.price)
            participant.shares_subtract(self.stock_symbol, self.amount)
            self.posted_by.balance_subtract(self.price)
            self.posted_by.shares_add(self.stock_symbol, self.amount)

class MarketOrder(Order):
    def price_matches(self, price):
        return True

class LimitOrder(Order):
    def __init__(self, amount, price, limit):
        super(amount, price)
        self.limit = limit

    def price_matches(self, price):
        if self.direction == Order.BUY:
            return self.price <= price and price <= self.limit
        elif self.direction == Order.SELL:
            return self.limit <= price and price <= self.price
