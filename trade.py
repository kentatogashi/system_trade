import configparser as cp
import os
import sys
import ccxt
import json
from datetime import datetime, timedelta, timezone
import requests
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
# LSTM prediction modules
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.layers.recurrent import LSTM
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
from keras import backend

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

    def get_ohlcv(self, before=500, timeframe='5m'):
        timestamp = self.exchange.fetch_ticker(self.ticker)['timestamp']
        timestamp_since = timestamp - before * (60 * 60 * 1000)
        candles = self.exchange.fetch_ohlcv(self.ticker, timeframe=timeframe, since=timestamp_since)
        return candles

    def get_ohlcv_by_cryptwatch(self, period=3600):
        url = 'https://api.cryptowat.ch/markets/bitflyer/btcjpy/ohlc?periods=%s' % (period)
        res = requests.get(url)
        data = res.json()['result'][str(period)]
        return data

    def predict_price(self, n=10):

        def make_datasets(df, maxlen=25):
            length_of_sequences = len(df)
            data = []
            target = []
            for i in range(0, length_of_sequences - maxlen):
                data.append(df.iloc[i:i+maxlen, 1])
                target.append(df.iloc[i+maxlen, 1])
            X = np.array(data).reshape(len(data), maxlen, 1)
            Y = np.array(target).reshape(len(data), 1)
            return (X, Y)

        def weight_variable(shape):
            return backend.truncated_normal(shape, stddev=0.1)

        data = self.get_ohlcv_by_cryptwatch()
        # Use only closing data
        df = pd.DataFrame(data, columns=['unixtime', 'o', 'h', 'l', 'c', 'v', 'other'])
        maxlen = 25
        X, Y = make_datasets(df, maxlen)
        train_rate = 0.9
        N_train = int(len(df) * train_rate)
        N_validation = len(df) - N_train
        X_train, X_validation, Y_train, Y_validation = \
                train_test_split(X, Y, test_size=N_validation)

        n_hidden = 4
        n_out = 1

        model = Sequential()
        model.add(LSTM(n_hidden, init=weight_variable, input_shape=(maxlen, n_out)))
        model.add(Dense(n_out, init=weight_variable))
        model.add(Activation(('linear')))
        optimizer = Adam(lr=0.0001, beta_1=0.9, beta_2=0.999)
        model.compile(loss='mean_squared_error', optimizer=optimizer)

        epochs = 100 
        batch_size = 10
        patience = 10

        early_stopping = EarlyStopping(patience=patience, verbose=1)
        model.fit(X_train, Y_train, batch_size=batch_size, epochs=epochs, validation_data=(X_validation, Y_validation), callbacks=[early_stopping])
        print(model.predict(X_validation))

    def checkOrder(self):
        raise NotImplementedError

if __name__ == '__main__':
    conf_file = 'trade.conf'
    trade = Trade(conf_file)
