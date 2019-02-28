# -*- coding:utf-8 -*-
"""
Statistical tools for time series analysis
"""
import datetime
import statsmodels.tsa.stattools as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


def testStationarity(ts):
    '''计算数据相关参数'''
    dftest = st.adfuller(ts)
    # 对上述函数求得的值进行语义描述
    dfoutput = pd.Series(dftest[0:4], index=[
                         'Test Statistic', 'p-value',
                         '#Lags Used', 'Number of Observations Used'])
    for key, value in dftest[4].items():
        dfoutput['Critical Value (%s)' % key] = value
    return dfoutput

# 自相关和偏相关图，默认阶数为31阶


def draw_acf_pacf(ts, lags=31):
    f = plt.figure(facecolor='white')
    ax1 = f.add_subplot(211)
    plot_acf(ts, lags=lags, ax=ax1)
    ax2 = f.add_subplot(212)
    plot_pacf(ts, lags=lags, ax=ax2)
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


def handleMissingData(data, start, end):
    time_indexS = pd.date_range(start=start, end=end, freq='5min')
    df = pd.DataFrame(columns=['upStatus', 'upSpeed',
                               'downStatus', 'downSpeed'])
    for index in time_indexS:
        if index in data.index:
            da = data.loc[index]
        else:
            print(index)
        df.loc[index] = da
    df.to_csv('./test30_all.csv')
    return df


def spiltUpSpeed(data):
    data = data.get('upSpeed')
    time = pd.date_range(start='00:00', end='23:55', freq='5min').time
    upSpeedData = pd.DataFrame(index=time)
    dayTime = data.index.strftime('%Y-%m-%d')
    pre_day = '0'
    for day in dayTime:
        if pre_day == day:
            continue
        else:
            pre_day = day
            daydf = data.loc[day].rename(day)
            daydf.index = time
            upSpeedData = pd.concat([upSpeedData, pd.DataFrame(daydf)],
                                    axis=1)
    upSpeedData.to_csv('./test30_upSpeed.csv')
    return upSpeedData


data = pd.read_csv("./test30_upSpeed.csv", index_col='timestamp')
# 此时dataindex不是datatimeindex类型
data.index = pd.date_range(start='00:00', end='23:55', freq='5min').time
# data.index = data_index    else:

# data.fillna(method='ffill')
# data = handleMissingData(data, start='11/1/2017 00:00',
#                   end='11/30/2017 23:55', freq='5min')
# spiltUpSpeed(data)
print(data.describe())

fig1 = plt.figure(facecolor='white', figsize=(10, 5))
ax1 = fig1.add_subplot(111)
# drawData = data.loc[:,['2017-11-07','2017-11-08','2017-11-09',
#                        '2017-11-14','2017-11-15','2017-11-16']]
drawData = data.loc[:, ['2017-11-07', '2017-11-08', '2017-11-09',
                        '2017-11-14', '2017-11-15', '2017-11-16']]
drawData = data
'''   =====   =======
      Alias   Color
      =====   =======
      'b'     blue
      'g'     green
      'r'     red
      'c'     cyan
      'm'     magenta
      'y'     yellow
      'k'     black
      'w'     white
      =====   =======  '''
color_tup = {'0': 'b', '1': 'g', '2': 'r',
             '3': 'c', '4': 'm', '5': 'y', '6': 'k'}
drawData['mean'] = np.mean(drawData, axis=1)
drawData['std'] = np.std(drawData, axis=1)
for column in drawData.columns:
    if(column == 'mean' or column == 'std'):
        ax1.plot(drawData.loc[:, [column]], label=column, linestyle='-')
    else:
        whatday = datetime.datetime.strptime(column, '%Y-%m-%d').strftime("%w")
        print(column, whatday)
        ax1.plot(drawData.loc[:, [column]], label=column,
                 linewidth=2, linestyle=':', color=color_tup[whatday])

plt.legend()
plt.show()
