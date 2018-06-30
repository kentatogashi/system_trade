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
        self.open_orders_limit = 1

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

    def get_symbols(self):
        return self.exchange.symbols

    def get_ticker(self):
        return self.exchange.fetchTicker(self.ticker)

    def get_historical_data(self, start_date=None, time_unit='1d'):
        if start_date is None:
            start_date = (datetime.now().replace(tzinfo=timezone.utc) - timedelta(days=14)).timestamp()
        historical_data = self.exchange.fetch_ohlcv(
                self.ticker, 
                timeframe=time_unit,
                since="20180626",
                limit=100)
        return historical_data

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
    print(trade.buy(amount=0.0001, price=100000))
    print(trade.sell(amount=0.0001, price=10000000))
