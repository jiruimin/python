# -*- coding:utf-8 -*-
import statsmodels.tsa.stattools as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import statsmodels.api as sm
from statsmodels.tsa.arima_model import ARIMA


# 移动平均图

def draw_trend(timeSeries, size):
    plt.figure(facecolor='white')
    # 对size个数据进行移动平均
    rol_mean = timeSeries.rolling(window=size).mean()
    # 对size个数据进行加权移动平均
    rol_weighted_mean = pd.ewma(timeSeries, span=size)

    timeSeries.plot(color='blue', label='Original')
    rol_mean.plot(color='red', label='Rolling Mean')
    rol_weighted_mean.plot(color='black', label='Weighted Rolling Mean')
    plt.legend(loc='best')
    plt.title('Rolling Mean')
    plt.show()


def draw_ts(timeSeries):
    plt.figure(facecolor='white')
    timeSeries.plot(color='blue')
    plt.show()


'''
　　Unit Root Test
   The null hypothesis of the Augmented Dickey-Fuller is that there is a unit
   root, with the alternative that there is no unit root. That is to say the
   bigger the p-value the more reason we assert that there is a unit root
'''


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
    dataset = data.iloc[0: len(data) - number]

    model = ARIMA(dataset, order=(2, 0, 0), freq='5min')
    # model = ARIMA(dataset, order=(2, 0, 0))
    result_arma = model.fit(trend='c')

    predict = result_arma.predict(
        start='2017-11-29 00:00:00', end='2017-11-30 23:55:00', dynamic=True)
    RMSE = np.sqrt(((predict - data[len(data) - number:])**2).sum() / (number))

    print(len(dataset))
    print(dataset)
    print(len(predict))
    print(predict)
    # predict.index = data.index[len(data) - number - 1:]
    plot_results(predict, data[len(data) - number * 2:])
    return predict, RMSE


def handleData(data, start, end, freq):
    data_index = pd.date_range(start=start, end=end, freq=freq)
    df = pd.DataFrame(index=data_index, columns=['upSpeed'])
    for index in data_index:
        if(index in data.index):
            da = data.loc[index]
        # df.append(pd.DataFrame(da, index=['name'], columns=['upSpeed']))
        df.loc[index] = da['upSpeed']
    return df


print(sm.datasets.sunspots.NOTE)
dta = sm.datasets.sunspots.load_pandas().data
dta.index = pd.Index(sm.tsa.datetools.dates_from_range('1700', '2008'))
del dta["YEAR"]
print(dta)
# dta.plot(figsize=(12, 8))
# plt.show()

# fig = plt.figure(figsize=(12, 8))
# ax1 = fig.add_subplot(211)
# fig = sm.graphics.tsa.plot_acf(dta.values.squeeze(), lags=40, ax=ax1)
# ax2 = fig.add_subplot(212)
# fig = sm.graphics.tsa.plot_pacf(dta, lags=40, ax=ax2)


arma_mod20 = sm.tsa.ARMA(dta, (2, 0)).fit(disp=False)
print(arma_mod20.params)
print(arma_mod20.aic, arma_mod20.bic, arma_mod20.hqic)
predict_sunspots = arma_mod20.predict('1800', '2108', dynamic=True)
plot_results(predict_sunspots, dta)
print(predict_sunspots)
plt.show()
