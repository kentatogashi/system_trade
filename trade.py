import ccxt
from datetime import datetime, timedelta, timezone

class Trade:
    def __init__(self, conf=None):
        if conf is None:
            self.conf = None
            self.ticker = 'BTC/JPY'
            self.exchange = ccxt.bitbank()
            self.exchange.apiKey = None
            self.exchange.secret = None
        else:
            self.conf = conf
            self.ticker = conf.ticker
            self.exchange = eval("ccxt.%s()" % conf.exchange)
            self.exchange.apiKey = conf.api_key
            self.exchange.secret = conf.secret

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

if __name__ == '__main__':
    trade = Trade()
    print(trade.get_symbols())
    print(trade.get_historical_data())
