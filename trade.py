import os
import sys
import ccxt
from datetime import datetime, timedelta, timezone

class Trade:
    def __init__(self, conf=None):
        if conf:
            self.ticker = conf.ticker
            self.exchange = eval("ccxt.%s()" % conf.exchange)
            self.exchange.apiKey = conf.API_KEY
            self.exchange.secret = conf.SECRET
        else:
            if os.environ.get('API_KEY'):
                self.exchange.apiKey = os.environ.get('API_KEY')
            else:
                sys.exit('not found API_KEY')
            if os.environ.get('SECRET'):
                self.exchange.secret = os.environ.get('SECRET')
            else:
                sys.exit('not found SECRET')
                
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

    def buy(self, amount, price):
        raise NotImplementedError

    def sell(self, amount, price):
        raise NotImplementedError

    def checkOrder(self):
        raise NotImplementedError

    def cancelPreviousOrder(self):
        raise NotImplementedError

    def public_api_example(self):
        result = self.exchange.fetch_markets()
        print(json.dumps(result, indent=True))
        print('fetch_ticker')
        result = self.exchange.fetch_ticker('BTC/JPY')
        print(json.dumps(result, indent=True))
        print('fetch_order_book')
        result = self.exchange.fetch_order_book(symbol='BTC/JPY')
        print(result)
        print('fetch_trades')
        result = self.exchange.fetch_trades(symbol='BTC/JPY', limit=2)
        print(result)

    def private_api_example(self):
        result = self.exchange.fetch_balance()
        print(json.dumps(result, indent=True))

if __name__ == '__main__':
    trade = Trade()
