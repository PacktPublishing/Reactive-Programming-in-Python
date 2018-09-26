import json
import os.path

from rx import Observable

def read_json(filename):
    with open(filename) as file:
        return json.load(file)

json_data = read_json('stock-data.json')
# Right now we are loading JSON data from a file, but the advantage of
# reactive programming is that the source of the Observable data can
# come from anywhere. In later videos we're going to be building a
# stock exchange desktop app and the stock data will be coming from a
# web server or from the client applications. What we do now in terms
# of filtering and mapping these observables can be applied and
# re-used later on.

# For the participants and stocks in the stock exchange, we're going
# to loop through them and print them out.
print('Stock Exchange Participants:')
Observable.from_(json_data['participants']).map(
    lambda participant: participant['name']).subscribe(
    lambda name: print('* {}'.format(name)))

print('\nStock Exchange Stocks:')
Observable.from_(json_data['stocks']).map(
    lambda stock: stock['name']).subscribe(
    lambda name: print('* {}'.format(name)))

# Now we're going to split the list of orders into two streams of
# data, one for the buy orders and one for the sell orders.
orders = Observable.from_(json_data['orders'])

# We also want to make sure the orders are not fulfilled, that they
# are open orders that a participant in the stock exchange can respond
# to. This will be useful later on when we're building the rest of our
# stock exchange app.
def is_open_order(order):
    return order['fulfilled'] == False

# To keep things simple, we'll just print out each order that matches
# our filters.
def print_open_order(order):
    fmt = '{posted_by} posted: {direction} {amount} x {stock_symbol} @ {price}'
    print(fmt.format(**order))

# First we get the open orders
open_orders = orders.filter(is_open_order)
print('\nOpen Orders:')

# Then we filter them into buy and sell orders and print them out
# immediately.
open_buy_orders = open_orders.filter(
    lambda order: order['direction'] == 'buy').subscribe(print_open_order)
open_sell_orders = open_orders.filter(
    lambda order: order['direction'] == 'sell').subscribe(print_open_order)
