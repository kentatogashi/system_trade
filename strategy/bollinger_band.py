import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def make_datasets(n=100, an=5):
    data = np.abs(np.random.randn(n))
    r_idx = np.random.randint(1, n, an)
    for i in r_idx:
        data[i] = data[i] + (data.mean() * 10)
    return pd.DataFrame(data)

def bollinger_band2(df, window=10):
    df_ma = df[0].rolling(window=window).mean()
    df_std = df[0].rolling(window=window).std()
    band2_upper = df_ma + 2 * df_std
    band2_lower = df_ma - 2 * df_std
    return (band2_upper, df_ma, band2_lower)

def plot_bollinger_band():
    df = make_datasets()
    u, m, l = bollinger_band2(df)
    ax = df[0].plot(color='blue', label='Data')
    m.plot(ax=ax, ls='--', color='red', label='Mean')
    u.plot(ax=ax, ls='--', color='green', label='Upper')
    l.plot(ax=ax, ls='--', color='green', label='Lower')
    ax.grid()
    ax.legend()
    plt.show()

if __name__ == '__main__':
  plot_bollinger_band()
