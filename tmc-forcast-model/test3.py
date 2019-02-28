# -*- coding:utf-8 -*-
import statsmodels.tsa.stattools as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import statsmodels.api as sm
# 移动平均图


def testStationarity(ts):
    dftest = st.adfuller(ts)
    # 对上述函数求得的值进行语义描述
    dfoutput = pd.Series(dftest[0:4], index=[
                         'Test Statistic',
                         'p-value',
                         '#Lags Used',
                         'Number of Observations Used'])
    for key, value in dftest[4].items():
        dfoutput['Critical Value (%s)' % key] = value
    return dfoutput

# 自相关和偏相关图，默认阶数为31阶


def draw_acf_pacf(ts, lags=31):
    f = plt.figure(facecolor='white')
    ax1 = f.add_subplot(211)
    plot_acf(ts, lags=31, ax=ax1)
    ax2 = f.add_subplot(212)
    plot_pacf(ts, lags=31, ax=ax2)
    plt.show()


def plot_results(predicted_data, true_data):
    fig = plt.figure(facecolor='white', figsize=(10, 5))
    ax = fig.add_subplot(111)
    ax.plot(true_data, label='True Data')
    plt.plot(predicted_data, label='Prediction')
    plt.legend()
    plt.show()


def arma_predict(data, number):
    # dataset = data.iloc[0: len(data) - number]
    dataset = data
    # result_arma = ARIMA(dataset, order=(2, 0, 2), freq='5min').fit(trend='c')
    # result_arma = sm.tsa.ARMA(dataset, order=(2, 2), freq='5min').fit()
    data_index = pd.date_range(start='12/1/2017 00:00',
                               end='12/2/2017 23:55',
                               freq='5min')
    # objSeries1 = pd.Series(range(len(data_index)), index=data_index)
    result_arma = sm.tsa.ARMA(dataset, order=(2, 2), freq='5min').fit()
    predict = result_arma.predict(exog=range(len(data_index)),
                                  start='2017-11-29 00:00:00',
                                  end='2017-12-1 23:55:00', dynamic=False)
    RMSE = np.sqrt(((predict - data[len(data) - number:])**2).sum() / (number))
    plot_results(predict, data[len(data) - number * 2:])
    return predict, RMSE


def handleData(data, start, end, freq):
    data_index = pd.date_range(start=start, end=end, freq=freq)
    df = pd.DataFrame(index=data_index, columns=['upSpeed'])
    for index in data_index:
        if(index in data.index):
            da = data.loc[index]
        df.loc[index] = da['upSpeed']
    return df


data = pd.read_csv("./test30.csv",
                   index_col='timestamp')      # 201711010000

data.index = pd.to_datetime(data.index, format='%Y%m%d%H%M')
data = handleData(data, start='11/1/2017 00:00',
                  end='11/30/2017 23:55', freq='5min')
data.index.freq = '5min'
# data.index = pd.to_datetime(data.index, format='%Y-%m')
# data.index.freq = 'MS'

series = data.loc[:, 'upSpeed']
# print(series)
print(testStationarity(series))

# re = arma_predict(series, 288)

fig1 = plt.figure(facecolor='white', figsize=(10, 5))
ax1 = fig1.add_subplot(111)
ax1.plot(series.loc['2017-11-7 00:00:00':'2017-11-7 23:55:00'],
         label='2017-11-7')
fig2 = plt.figure(facecolor='red', figsize=(10, 5))
ax2 = fig2.add_subplot(212)
ax1.plot(series.loc['2017-11-8 00:00:00':'2017-11-8 23:55:00'],
         label='2017-11-8')
plt.legend()
plt.show()
