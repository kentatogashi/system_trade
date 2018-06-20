import ccxt

class Trade:
    def __init__(self, conf):
        self.conf = conf
        self.ticker = conf.ticker
        self.exchange = eval("ccxt.%s()" % conf.exchange)
        self.exchange.apiKey = conf.api_key
        self.exchange.secret = conf.secret

    def get_ticker():
        return self.exchange.fetchTicker(self.ticker)

    def buy(self, amount, price):
        raise NotImplementedError

    def sell(self, amount, price):
        raise NotImplementedError

    def checkOrder(self):
        raise NotImplementedError

    def cancelPreviousOrder(self):
        raise NotImplementedError
