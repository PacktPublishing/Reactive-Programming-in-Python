from itertools import groupby

from rx import Observable

from client.client import Client

def order_is_valid(order):
    symbol = order.get('symbol', '')#.replace(' ', '')
    if symbol is None:
        return False
    symbol = symbol.replace(' ', '')
    price = order.get('price', 0)
    if symbol != '' and price >= 0.01:
        return True
    return False

def parse_stock_from_msg(msg):
    msg = msg.split(' ')
    fulfilled = msg[0] == 'fulfilled:'
    fulfilled_by = None
    if fulfilled:
        fulfilled_by = msg[1].replace(':', '')
    return {
        'direction': msg[2],
        'stock_symbol': msg[3],
        'quantity': int(msg[4]),
        'price': float(msg[6].replace('$', '')),
        'fulfilled': fulfilled,
        'fulfilled_by': fulfilled_by,
    }

def write_order(client, order):
    msg = 'order,0,{},{},{},{}'.format(
        order['stock_symbol'],
        order['direction'],
        order['quantity'],
        order['price'],
    )
    client.write_message(msg)

def run_client_websocket(client, stock_prices):
    """
    Creates a websocket client connection and whenever orders are received,
    groups them by stock symbol and aggregates them

    :param client: a Client
    :param stock_prices: a Subject
    """
    def update(stock_updates):
        if len(stock_updates) == 0:
            return
        for stock_update in stock_updates:
            stock_prices.on_next(stock_update)
    aggregate_stock_orders_from_messages(client.messages).subscribe(update)
    client.connect()

def aggregate_stock_orders_from_messages(observable):
    """
    :param observable: an Observable emitting messages from the stock exchange server
    :return: an Observable
    """
    return observable \
        .map(parse_stock_from_msg) \
        .buffer_with_time(100) \
        .map(find_prices)

def find_prices(all_orders):
    prices = []
    for stock_symbol, orders in group_orders(all_orders).items():
        buy = fold_price_of_filtered_orders(max, 'buy', orders)
        sell = fold_price_of_filtered_orders(min, 'sell', orders)
        prices.append((stock_symbol, stock_symbol, buy, sell))
    return prices

def group_orders(orders):
    result = {}
    groups = groupby(orders, key=lambda order: order['stock_symbol'])
    for stock_symbol, group in groups:
        result[stock_symbol] = list(group)
    return result

def fold_price_of_filtered_orders(aggregate, direction, orders, default=1.0):
    """
    Fold prices of given orders into one value

    :param aggregate: a function for reducing into one number, such as min or max
    :param direction: a 'buy' or 'sell' order
    :param orders: an iterator containing orders
    :param default: if there are no orders to aggregate, returns this value
    :return: a float, the aggregate/reduced/folded price
    """
    filtered_orders = filter_orders(direction, orders)
    if len(filtered_orders) == 0:
        return default
    order = aggregate(filtered_orders, key=lambda order: order['price'])
    return order['price']

def filter_orders(direction, orders):
    return list(filter(compare_order(direction), orders))

def compare_order(direction):
    def compare(order):
        return order['direction'] == direction
    return compare
