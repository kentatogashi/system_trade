import configparser as cp
import os
import sys
import ccxt
import json
from datetime import datetime, timedelta, timezone

class LimitOrderError(Exception):
    pass

class Trade:
    def __init__(self, conf_file=None):
        conf = cp.ConfigParser()
        conf.read(conf_file, 'UTF-8')
        self.ticker = conf.get('setting', 'ticker')
        self.exchange = eval("ccxt.%s()" % conf.get('setting', 'exchange'))
        self.exchange.apiKey = conf.get('setting', 'api_key')
        self.exchange.secret = conf.get('setting', 'secret')
        self.open_orders_limit = 10

    def order_is_enable(self):
        open_orders = self.exchange.fetch_open_orders(symbol=self.ticker)
        if self.open_orders_limit > len(open_orders):
            return True
        return False

    def buy(self, amount, price, _type='limit'):
        if self.order_is_enable():
            result = self.exchange.create_order(
                    symbol=self.ticker, type=_type, 
                    side='buy', amount=amount, price=price)
            return json.dumps(result, indent=True)
        else:
            raise LimitOrderError

    def sell(self, amount, price, _type='limit'):
        if self.order_is_enable():
            result = self.exchange.create_order(
                    symbol=self.ticker, type=_type, 
                    side='sell', amount=amount, price=price)
            return json.dumps(result, indent=True)
        else:
            raise LimitOrderError

    def cancel_previous_order(self):
        orders = self.exchange.fetch_open_orders(self.ticker)
        if len(orders) == 0:
            return False
        else:
            sorted_ids = sorted(orders, key=lambda x: x['id'])
            previous_order_id = [int(x['id']) for x in sorted_ids][-1]
            self.exchange.cancel_order(previous_order_id, self.ticker)
            return True

    def get_symbols(self):
        return self.exchange.symbols

    def get_ticker(self):
        return self.exchange.fetchTicker(self.ticker)

    def get_ohlcv(self, before=10, timeframe='1h'):
        timestamp = self.exchange.fetch_ticker(self.ticker)['timestamp']
        timestamp_since = timestamp - before * (60 * 60 * 1000)
        candles = self.exchange.fetch_ohlcv(self.ticker, timeframe=timeframe, since=timestamp_since)
        return candles

    def checkOrder(self):
        raise NotImplementedError

    def cancelPreviousOrder(self):
        raise NotImplementedError

    def public_api_example(self):
        result = self.exchange.fetch_markets()
        print(json.dumps(result, indent=True))
        print('fetch_ticker')
        result = self.exchange.fetch_ticker(self.ticker)
        print(json.dumps(result, indent=True))
        print('fetch_order_book')
        result = self.exchange.fetch_order_book(symbol=self.ticker)
        print(result)
        print('fetch_trades')
        result = self.exchange.fetch_trades(symbol=self.ticker, limit=2)
        print(result)

    def private_api_example(self):
        result = self.exchange.fetch_balance()
        print(json.dumps(result, indent=True))

if __name__ == '__main__':
    conf_file = 'trade.conf'
    trade = Trade(conf_file)
    #trade.buy(amount=0.0001, price=100000)
    #import time
    #time.sleep(5)
    #trade.cancel_previous_order()
    print(trade.get_ohlcv())
