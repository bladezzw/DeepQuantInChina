# encoding: utf-8
"""
Created on Fri Mar  3 09:44:49 2017
此文档的feature中的带"_talib"后缀用来搞论文
思路:
1.要么都用talib,(但是计算新一个特征bar(未输入GPU)的时间可能会随特征图变大而增加计算时间。可用多进程解决，
但肯定不够股票软件的特征计算模式快);
2.要么与股票软件一样,用它的计算方法.(计算新一个特征bar每一个特征只用计算一次)
**最好也实现股票软件的计算形式(即,计算新一个特征bar每一个特征只用计算一次)**
3.需要 TODO 把OHLCV先标准化归一化吗?
4.TODO:检查每个feature看有没有inf, 全0, 全1, 全同样的.
5.TODO:对某些函数增加timelag,并加入featuresmap.
@author: bladez
"""
import time
from numba import jit
import numpy as np
# %%work of import
import pandas as pd
# import pandas.io.data as web
# import pandas_datareader as pdr
import talib as ta

import matplotlib.pyplot as plt


def exc_time(func, *args, **kwargs):
    """
    计算运行时间
    :param func: a function
    :param args: arguements of the function
    :param kwargs: arguements of the function
    :return: time costs on running the function
    """

    def wrapper(func, *args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        stop_time = time.time()
        print("run time is %s" % (stop_time - start_time))

    return wrapper(func, *args, **kwargs)


def plot1lines(Series):
    plt.figure(figsize=[15, 10])
    if Series.__len__() > 10:  # 如果只有一列
        plt.plot(Series)
    else:  # 如果有多列
        for col in Series.__iter__():
            plt.plot(col)
    plt.show()


class features(object):
    """
    features of OHLCV of a stock or future
    """

    def __init__(self, open, high, low, close, volume):
        self.open = np.array(open).astype('float64')
        self.high = np.array(high).astype('float64')
        self.low = np.array(low).astype('float64')
        self.close = np.array(close).astype('float64')
        self.volume = np.array(volume).astype('float64')
        self.featuresmap = np.array([open, high, low, close])
        self.__allfeatures__ = ['ACOS_talib', 'ADD_talib', 'ADOSC_talib', 'ADX_talib', 'AD_talib', 'APO_talib',
                                'AROONOSC_talib', 'AROON_talib', 'ATAN_talib', 'ATR_talib', 'AVGPRICE_talib',
                                'BBands_talib', 'BOR_talib', 'CCI_talib', 'CDL2CROWS_talib', 'CDL3BLACKCROWS_talib',
                                'CDL3INSIDE_talib', 'CDL3LINESTRIKE_talib', 'CDL3OUTSIDE_talib',
                                'CDL3WHITESOLDIERS_talib',
                                'CDLADVANCEBLOCK_talib', 'CDLBELTHOLD_talib', 'CDLBREAKAWAY_talib',
                                'CDLCLOSINGMARUBOZU_talib',
                                'CDLCONCEALBABYSWALL_talib', 'CDLCOUNTERATTACK_talib', 'CDLDARKCLOUDCOVER_talib',
                                'CDLDOJISTAR_talib', 'CDLDOJI_talib', 'CDLDRAGONFLYDOJI_talib',
                                'CDLENGULFING_talib', 'CDLEVENINGDOJISTAR_talib', 'CDLEVENINGSTAR_talib',
                                'CDLGAPSIDESIDEWHITE_talib', 'CDLGRAVESTONEDOJI_talib', 'CDLHAMMER_talib',
                                'CDLHANGINGMAN_talib',
                                'CDLHARAMICROSS_talib', 'CDLHARAMI_talib', 'CDLHIGHWAVE_talib', 'CDLHIKKAKEMOD_talib',
                                'CDLHIKKAKE_talib', 'CDLHOMINGPIGEON_talib', 'CDLIDENTICAL3CROWS_talib',
                                'CDLINNECK_talib',
                                'CDLINVERTEDHAMMER_talib', 'CDLKICKINGBYLENGTH_talib', 'CDLKICKING_talib',
                                'CDLLADDERBOTTOM_talib', 'CDLLONGLEGGEDDOJI_talib', 'CDLLONGLINE_talib',
                                'CDLMARUBOZU_talib',
                                'CDLMATCHINGLOW_talib', 'CDLMATHOLD_talib', 'CDLMORNINGDOJISTAR_talib',
                                'CDLMORNINGSTAR_talib',
                                'CDLONNECK_talib', 'CDLPIERCING_talib', 'CDLRICKSHAWMAN_talib',
                                'CDLRISEFALL3METHODS_talib',
                                'CDLSEPARATINGLINES_talib', 'CDLSHOOTINGSTAR_talib', 'CDLSHORTLINE_talib',
                                'CDLSPINNINGTOP_talib', 'CDLSTALLEDPATTERN_talib', 'CDLSTICKSANDWICH_talib',
                                'CDLTAKURI_talib', 'CDLTASUKIGAP_talib', 'CDLTHRUSTING_talib', 'CDLTRISTAR_talib',
                                'CDLUNIQUE3RIVER_talib', 'CDLUPSIDEGAP2CROWS_talib', 'CDLXSIDEGAP3METHODS_talib',
                                'CMO_talib',
                                'COSH_talib', 'COS_talib', 'DEMA_talib', 'DIV_talib', 'DI_talib', 'DMI_talib',
                                'DM_talib', 'EMA', 'EMA_talib', 'EXP_talib', 'HT_DCPERIOD_talib', 'HT_DCPHASE_talib',
                                'HT_PHASOR_talib', 'HT_SINE_talib', 'HT_TRENDMODE_talib', 'HT_talib', 'KAMA_talib',
                                'KD_talib', 'LN_talib', 'LOG10_talib', 'MACD_talib', 'MAXINDEX_talib',
                                'MAX_talib', 'MA_talib', 'MEDPRICE_talib', 'MFI_talib', 'MIDPEICE_talib',
                                'MININDEX_talib', 'MOM_talib', 'MULT_talib', 'NATR_talib', 'OBV_talib', 'PPO_talib',
                                'ROC_talib', 'RSI_talib', 'SAR_talib', 'SINH_talib', 'SIN_talib', 'SQRT_talib',
                                'SUB_talib',
                                'TANH_talib', 'TAN_talib', 'TRANGE_talib', 'TRIX_talib',
                                'TSF_talib', 'TYPPRICE_talib', 'ULTOSC_talib', 'VAR_talib', 'WCLPRICE_talib',
                                'WILLIAMS_talib', 'WMA_talib', 'CORREL_talib', 'HT_TRENDMODE_talib',
                                'linearreg_talib', 'stddev_talib']

    @jit
    def normalizing(self, a=None):
        """
        正态标准化
        :param a:
        :return:
        """
        if a:
            a = np.array(a).astype('float64')
            std_a = a.std()
            mean_a = a.mean()
            temp = (a - mean_a) / std_a
            return temp

    @jit
    def normal_ones(self, a=None):
        """
        正太标准化后,归一化
        :param a:
        :return:
        """
        if a is not None:
            std_a = a.std()
            mean_a = a.mean()
            temp = (a - mean_a) / std_a
            temp0 = temp / max(temp)
            return temp0

    # def self_dict(self):
    #     """
    #     没啥用,只是用来看看比object类多出的新方法
    #     :return:
    #     """
    #     a = set(self.__dict__)
    #     b = set(object.__dict__)
    #     attr_name = 'self_dict'
    #     attr_value = a - b
    #     self.__setattr__(attr_name, attr_value)
    #     return a - b

    # -------------------------------Overlap Studies--------------------------------#
    # @property
    # def SMA(self, Series=[], N=5, w=1):
    #     """
    #     简单移动平均,与股票软件上一样，检验通过,包含前面N个值
    #     SMA(Close,N,W weight):Close的N日移动平均,weight为权重,如Y[i]=( Y[i-1]*(N-W) + X*W )/N
    #     :param Close: pd.Series ,float
    #     :param N: int
    #     :param weight:
    #     :return: sma
    #     """
    #     if not Series:
    #         Series = self.close
    #     y0 = list(Series)
    #     sma = y0[0:N - 1]  # set the head N bar of close on sma, otherwise head'N of sma are None
    #     [sma.append((sma[i - 1] * (N - w) + y0[i] * w) / N) for i in range(len(y0)) if i >= N - 1]
    #     attr_name = "SMA" + str(N)
    #     # attr_value = pd.Series(sma, name=attr_name)
    #     attr_value = sma
    #     self.__setattr__(attr_name, attr_value)
    #     return attr_value

    def MA_talib(self, Series=[], N=5):
        """
        简单平均,与股票软件上一样，检验通过，默认没有前面N个值
        :param args:  N:ndays
        :param kwargs:
        :return: ta.MA(*args,**kwargs)
        """
        if not Series:
            Series = self.close

        attr_name = "MA_talib" + str(N)
        attr_value = ta.MA(Series, N)
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    def EMA_talib(self, Series=[], N=12):  # undone
        """
        EMA(X,N):X的N日指数移动平均.股票软件上的算法:Y[i]=(X*2+Y[i-1]*(N-1))/(N+1)
        结果数列前面的一些数据跟股票软件上还是有不同，后面的趋于一致
        :param N: int
        :return: EXPMA
        """
        if not Series:
            Series = self.close

        Y = ta.EMA(Series, N)
        attr_name = "EMA" + str(N)
        attr_value = Y
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    def EMA(self, Series=[], N=12):  # undone
        """
        与股票软件上一样，检验通过，包含前面N个值
        EMA(X,N):X的N日指数移动平均.股票软件上的算法:Y[i]=(X*2+Y[i-1]*(N-1))/(N+1)
        :param N: int
        :return: EXPMA
        """
        if not Series:
            Series = self.close

        len_close = len(Series)
        Y = np.zeros(len_close)
        Y[0] = Series[0]
        for i in range(1, len_close):
            Y[i] = (Series[i] * 2 + Y[i - 1] * (N - 1)) / (N + 1)
        attr_name = "EMA" + str(N)
        attr_value = Y
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    def BBands_talib(self, Series=[], ndays=5.):
        """
        布林线:
        :param Series: 输入的数据列
        :param ndays: 时间间隔timeperiod int
        :return: 返回上中下boll线3个时间序列
        """
        if not Series:
            Series = self.close
        upperband, middleband, lowerband = ta.BBANDS(Series, timeperiod=ndays, nbdevup=2., nbdevdn=2., matype=0.)
        attr_name1 = "BBupperband" + str(ndays)
        attr_name2 = "BBmiddleband" + str(ndays)
        attr_name3 = "BBlowerband" + str(ndays)
        attr_value1 = upperband
        attr_value2 = middleband
        attr_value3 = lowerband
        # self.__setattr__(attr_name1, attr_value1)
        # self.__setattr__(attr_name2, attr_value2)
        # self.__setattr__(attr_name3, attr_value3)
        bb = np.array([attr_value1, attr_value2, attr_value3])
        return bb

    def DEMA_talib(self, Series=[], ndays=20):
        """
        双移动平均线(double exponential moving average)
        :param Series:
        :param ndays: int
        :return: DEMA
        """
        if not Series:
            Series = self.close
        real = ta.DEMA(Series, ndays)
        attr_name = "DEMA" + str(ndays)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    def HT_talib(self):
        """
        函数名：HT_TRENDLINE
        名称： 希尔伯特瞬时变换
        简介：是一种趋向类指标，其构造原理是仍然对价格收盘价进行算术平均，
        并根据计算结果来进行分析，用于判断价格未来走势的变动趋势
        :return:
        """
        real = ta.HT_TRENDLINE(self.close)
        attr_name = "HT_TRENDLINE"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    def KAMA_talib(self, Series=[], ndays=20):
        """
        考夫曼的自适应移动平均线
        :param Series:
        :param ndays: int
        :return:
        """
        if not Series:
            Series = self.close
        real = ta.KAMA(Series, ndays)
        attr_name = "KAMA" + str(ndays)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    def WMA_talib(self, Series=[], ndays=20):
        """
        Weighted Moving Average 移动加权平均法.
        以每次进货的成本加上原有库存存货的成本，除以每次进货数量与原有库存存货的数量之和，
        据以计算加权平均单位成本，以此为基础计算当月发出存货的成本和期末存货的成本的一种方法
        :param Series:
        :param ndays:
        :return:
        """
        if not Series:
            Series = self.close
        real = ta.WMA(Series, timeperiod=ndays)
        attr_name = "WMA" + str(ndays)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    # ------------------------ 需要 high和low ----------------------------#
    def MIDPEICE_talib(self, ndays=10):
        """
        Midpoint Price over period 中间价格的平均
        :param ndays:
        :return:
        """
        real = ta.MIDPRICE(self.high, self.low, ndays)
        attr_name = "MIDPRICE" + str(ndays)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    def SAR_talib(self, accel=0.02):
        """
        抛物线指标
        :param accel:
        :return:
        """
        real = ta.SAR(self.high, self.low, acceleration=accel, maximum=0.2)
        attr_name = "SAR" + str(accel)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    # -------------------------------Momentum Inicators--------------------------------#
    def ADX_talib(self, ndays=10):
        """
        平均趋向指数
        :param ndays:
        :return:
        """
        real = ta.ADX(self.high, self.low, self.close, timeperiod=ndays)
        attr_name = "ADX" + str(ndays)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    def APO_talib(self, Series=[], fast=12, slow=26):
        """

        :param fast: int
        :param slow: int
        :return:
        """
        if not Series:
            Series = self.close
        real = ta.APO(Series, fastperiod=fast, slowperiod=slow, matype=0)
        attr_name = "APO" + '_' + str(fast) + '_' + str(slow)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return attr_value

    def AROON_talib(self, ndays=10):
        """
        阿隆指标:通过计算自价格达到近期最高值和最低值以来所经过的期间数，阿
        隆指标帮助你预测价格趋势到趋势区域（或者反过来，从趋势区域到趋势）的变化。
        :param ndays: int
        :return:
        """
        aroondown, aroonup = ta.AROON(high, low, timeperiod=ndays)
        attr_name1 = "aroondown" + str(ndays)
        attr_name2 = "aroonup" + str(ndays)
        attr_value1 = aroondown
        attr_value2 = aroonup
        # self.__setattr__(attr_name1, attr_value1)
        # self.__setattr__(attr_name2, attr_value2)
        val = np.array([attr_value1, attr_value2])
        return val

    def AROONOSC_talib(self, ndays=10):
        """

        :param ndays:
        :return:
        """
        real = ta.AROONOSC(self.high, self.low, timeperiod=ndays)
        attr_name = "AROONOSC" + str(ndays)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def BOR_talib(self):
        """Balance Of Power 均势"""
        real = ta.BOP(self.open, self.high, self.low, self.close)
        attr_name = "APO"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CCI_talib(self, ndays=10):
        """
        CCI指标专门测量股价是否已超出常态分布范围
        :param ndays:
        :return:
        """
        real = ta.CCI(self.high, self.low, self.close, timeperiod=ndays)
        attr_name = "CCI" + str(ndays)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CMO_talib(self, Series=[], ndays=10):
        """
        CMO:Chande Momentum Oscillator 钱德动量摆动指标.计算公式：CMO=（Su－Sd）*100/（Su+Sd）
        :param ndays:
        :return:
        """
        if not Series:
            Series = self.close
        real = ta.CMO(Series, ndays)
        attr_name = "CMO" + str(ndays)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def DMI_talib(self, ndays=10):
        """
        DMI/DX动向指标或趋向指标
        :param ndays:
        :return:
        """
        real = ta.DX(self.high, self.low, self.close, timeperiod=ndays)
        attr_name = "DMI" + str(ndays)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def MACD_talib(self, fast=12, slow=26):
        """
        Moving Average Convergence/Divergence平滑异同移动平均线
        :param fast:
        :param slow:
        :param signal:
        :return:
        """
        macd, macdsignal, macdhist = ta.MACD(self.close, fast, slow)
        attr_name1 = "macd" + str(fast) + '_' + str(slow)
        attr_name2 = "macdsignal" + str(fast) + '_' + str(slow)
        attr_name3 = "macdhist" + str(fast) + '_' + str(slow)
        # attr_value1 = pd.Series(upperband, name=attr_name1)
        # attr_value2 = pd.Series(middleband, name=attr_name2)
        # attr_value3 = pd.Series(lowerband, name=attr_name3)
        attr_value1 = macd
        attr_value2 = macdsignal
        attr_value3 = macdhist
        # self.__setattr__(attr_name1, attr_value1)
        # self.__setattr__(attr_name2, attr_value2)
        # self.__setattr__(attr_name3, attr_value3)
        val = np.array([attr_value1, attr_value2, attr_value3])
        return val

    def MFI_talib(self, ndays=10):
        """
        MFI - Money Flow Index 资金流量指标,属于量价类指标，反映市场的运行趋势
        :param ndays:
        :return:
        """
        real = ta.MFI(self.high, self.low, self.close, self.volume, timeperiod=ndays)
        attr_name = "MFI" + str(ndays)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def DI_talib(self, ndays=10):
        """
        Minus Directional Indicator, DMI 中的DI指标 负方向指标
        :param ndays:
        :return:
        """
        real = ta.MINUS_DI(self.high, self.low, self.close, timeperiod=ndays)
        attr_name = "DI" + str(ndays)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def DM_talib(self, ndays=10):
        """
        Minus Directional Movement, DMI中的DM代表正趋向变动值即上升动向值
        :param ndays:
        :return:
        """
        real = ta.MINUS_DM(self.high, self.low, timeperiod=ndays)
        attr_name = "DM" + str(ndays)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def MOM_talib(self, Series=[], ndays=10):
        """
        Momentum 动量, 上升动向值
        :param Series:
        :param ndays:
        :return:
        """
        if not Series:
            Series = self.close
        real = ta.MOM(Series, timeperiod=ndays)
        attr_name = "MOM" + str(ndays)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def PPO_talib(self, fast=12, slow=26):
        """
        Percentage Price Oscillator 价格震荡百分比指数,和MACD指标非常接近的指标
        :param fast:
        :param slow:
        :return:
        """
        real = ta.PPO(self.close, fast, slow, matype=0)
        attr_name = "PPO" + str(fast) + '_' + str(slow)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def ROC_talib(self, ndays=10):
        """
        Rate of change : ((price/prevPrice)-1)*100 变动率指标
        :param ndays:
        :return:
        """
        real = ta.ROC(self.close, timeperiod=ndays)
        attr_name = "ROC" + str(ndays)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def RSI_talib(self, ndays=10):
        """
        Relative Strength Index 相对强弱指数
        :param ndays:
        :return:
        """
        real = ta.RSI(self.close, timeperiod=ndays)
        attr_name = "RSI" + str(ndays)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def KD_talib(self):
        """

        :return:
        """
        slowk, slowd = ta.STOCH(self.high, self.low, self.close, fastk_period=5, slowk_period=3, slowk_matype=0,
                                slowd_period=3,
                                slowd_matype=0)
        attr_name1 = "slowk"
        attr_name2 = "slowd"
        # attr_value1 = pd.Series(upperband, name=attr_name1)
        # attr_value2 = pd.Series(middleband, name=attr_name2)
        # attr_value3 = pd.Series(lowerband, name=attr_name3)
        attr_value1 = slowk
        attr_value2 = slowd
        # self.__setattr__(attr_name1, attr_value1)
        # self.__setattr__(attr_name2, attr_value2)
        val = np.array([attr_value1, attr_value2])
        return val

    def TRIX_talib(self, ndays=20):
        """
         Rate-Of-Change (ROC) of a Triple Smooth EMA
        :param ndays:
        :return:
        """
        real = ta.TRIX(self.close, timeperiod=ndays)
        attr_name = "TRIX" + str(ndays)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def ULTOSC_talib(self, fast=5, slow=10, timeperiod=28):
        """
        ULTOSC,Ultimate Oscillator 终极波动指标
        :param fast:
        :param slow:
        :param timeperiod:
        :return:
        """
        real = ta.ULTOSC(self.high, self.low, self.close, timeperiod1=fast, timeperiod2=slow, timeperiod3=timeperiod)
        attr_name = "ULTOSC" + str(fast) + '_' + str(slow)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def WILLIAMS_talib(self, ndays=10):
        """
        Williams' %R 威廉指标, WMS表示的是市场处于超买还是超卖状态
        :param ndays:
        :return:
        """
        real = ta.WILLR(self.high, self.low, self.close, timeperiod=ndays)
        attr_name = "WILLIAMS" + str(ndays)
        # attr_value = pd.Series(real, name=attr_name)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    # -----------------------------Volume Inicators--------------------------------#
    def AD_talib(self):
        """
        Chaikin A/D Line 累积/派发线(Accumulation/Distribution Line)
        Marc Chaikin提出的一种平衡交易量指标，以当日的收盘价位来估算成交流量，用于估定一段时间内该证券累积的资金流量。
        :return:
        """
        real = ta.AD(self.high, self.low, self.close, self.volume)
        attr_name = "AD"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def ADOSC_talib(self, fastperiod=3, slowperiod=10):
        """
        Chaikin A/D Oscillator Chaikin震荡指标
        将资金流动情况与价格行为相对比，检测市场中资金流入和流出的情况
        :return:
        """
        real = ta.ADOSC(self.high, self.low, self.close, self.volume, fastperiod=fastperiod, slowperiod=slowperiod)
        attr_name = "ADOSC" + '_' + str(fastperiod) + '_' + str(slowperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def OBV_talib(self):
        """
        TODO:解决Exception: input array type is not double
        On Balance Volume 能量潮
        Joe Granville提出，通过统计成交量变动的趋势推测股价趋势
        :return:
        """
        real = ta.OBV(self.close, self.volume)
        attr_name = "OBV"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    # -------------------------------Volatility Indicators--------------------------------#
    def ATR_talib(self, timeperiod=10):
        """
        真实波动幅度均值
        :param timeperiod:
        :return:
        """
        real = ta.ATR(self.high, self.low, self.close, timeperiod=timeperiod)
        attr_name = "ATR" + str(timeperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def NATR_talib(self, timeperiod=10):
        """
        归一化波动幅度均值
        :param timeperiod:
        :return:
        """
        real = ta.NATR(self.high, self.low, self.close, timeperiod=timeperiod)
        attr_name = "NATR" + str(timeperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def TRANGE_talib(self):
        """
        真正的范围
        :return:
        """
        real = ta.TRANGE(self.high, self.low, self.close)
        attr_name = "TRANGE"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    # -------------------------------Price Transform Inicators--------------------------------#
    def AVGPRICE_talib(self):
        """
        平均价格函数
        :return:
        """
        real = ta.AVGPRICE(self.open, self.high, self.low, self.close)
        attr_name = "AVGPRICE"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def MEDPRICE_talib(self):
        """
        中位数价格
        :return:
        """
        real = ta.MEDPRICE(self.high, self.low)
        attr_name = "MEDPRICE"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def TYPPRICE_talib(self):
        """
        代表性价格
        :return:
        """
        real = ta.TYPPRICE(self.high, self.low, self.close)
        attr_name = "TYPPRICE"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def WCLPRICE_talib(self):
        """
        加权收盘价
        :return:
        """
        real = ta.WCLPRICE(self.high, self.low, self.close)
        attr_name = "WCLPRICE"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    # -------------------------------Cycle Indicators--------------------------------#
    def HT_DCPERIOD_talib(self):
        """
         希尔伯特变换-主导周期,将价格作为信息信号，计算价格处在的周期的位置，作为择时的依据.
        :return:
        """
        real = ta.HT_DCPERIOD(self.close)
        attr_name = "HT_DCPERIOD"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def HT_DCPHASE_talib(self):
        """
        希尔伯特变换-主导循环阶段
        :return:
        """
        real = ta.HT_DCPHASE(self.close)
        attr_name = "HT_DCPHASE"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def HT_PHASOR_talib(self):
        """
        希尔伯特变换-希尔伯特变换相量分量
        :return:
        """
        inphase, quadrature = ta.HT_PHASOR(self.close)
        attr_name1 = "inphase"
        attr_name2 = "quadrature"
        # attr_value1 = pd.Series(upperband, name=attr_name1)
        # attr_value2 = pd.Series(middleband, name=attr_name2)
        # attr_value3 = pd.Series(lowerband, name=attr_name3)
        attr_value1 = inphase
        attr_value2 = quadrature
        # self.__setattr__(attr_name1, attr_value1)
        # self.__setattr__(attr_name2, attr_value2)
        val = np.array([attr_value1, attr_value2])
        return val

    def HT_SINE_talib(self):
        """
        希尔伯特变换-正弦波
        :return:
        """
        sine, leadsine = ta.HT_SINE(self.close)
        attr_name1 = "sine"
        attr_name2 = "leadsine"
        # attr_value1 = pd.Series(upperband, name=attr_name1)
        # attr_value2 = pd.Series(middleband, name=attr_name2)
        # attr_value3 = pd.Series(lowerband, name=attr_name3)
        attr_value1 = sine
        attr_value2 = leadsine
        # self.__setattr__(attr_name1, attr_value1)
        # self.__setattr__(attr_name2, attr_value2)
        val = np.array([attr_value1, attr_value2])
        return val

    def HT_TRENDMODE_talib(self):
        """
         希尔伯特变换-趋势与周期模式
        :return:
        """
        integer = ta.HT_TRENDMODE(self.close)
        attr_name = "HT_TRENDMODE_talib"
        attr_value = integer
        # self.__setattr__(attr_name, attr_value)
        return integer

    # -------------------------------Statistic Functions 统计学指标--------------------------------#

    def CORREL_talib(self, timeperiod=20):
        """
        皮尔逊相关系数
        :return:
        """
        real = ta.CORREL(self.high, self.low, timeperiod=timeperiod)
        attr_name = "CORREL_talib" + str(timeperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def linearreg_talib(self, timeperiod=10):
        """
        线性回归
        :param timeperiod:
        :return:
        """
        real = ta.LINEARREG(self.close, timeperiod=timeperiod)
        attr_name = "linearreg_talib" + str(timeperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def stddev_talib(self, timeperiod=5, nbdev=1):
        """

        :param timeperiod:
        :param nbdev:
        :return:
        """
        real = ta.STDDEV(self.close, timeperiod=timeperiod, nbdev=nbdev)
        attr_name = "stddev_talib" + str(timeperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def TSF_talib(self, timeperiod=10):
        """

        :param timeperiod:
        :return:
        """
        real = ta.TSF(self.close, timeperiod=timeperiod)
        attr_name = "TSF_talib" + str(timeperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def VAR_talib(self, timeperiod=5, nbdev=1):
        """

        :param timeperiod:
        :param nbdev:
        :return:
        """
        real = ta.VAR(self.close, timeperiod=timeperiod, nbdev=nbdev)
        attr_name = "VAR_talib" + str(timeperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    # -------------------------------Math Transform Functions--------------------------------#

    def ACOS_talib(self, Series=None):
        """
        反余弦函数，三角函数(定义域为(-1,1),在未归一化标准化前提下,用不了)
        :return:
        """
        if not Series:
            Series = self.normal_ones(self.close)
            real = ta.ACOS(Series)
            attr_name = "ACOS_talib"
            attr_value = real
            # self.__setattr__(attr_name, attr_value)
            return real
        else:
            Series = self.normal_ones(np.array(Series).astype('float64'))
            real = ta.ACOS(Series)
            attr_name = "ACOS_talib"
            attr_value = real
            # self.__setattr__(attr_name, attr_value)
            return real

    def ASIN_talib(self):
        """
        反正弦函数，三角函数
        :return:
        """
        real = ta.ASIN(self.close)
        attr_name = "ASIN_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def ATAN_talib(self):
        """

        :return:
        """
        real = ta.ATAN(self.close)
        attr_name = "ATAN_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def COS_talib(self):
        """
        余弦函数，三角函数
        :return:
        """
        real = ta.COS(self.close)
        attr_name = "COS_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def COSH_talib(self):
        """

        :return:
        """
        real = ta.COSH(self.close)
        attr_name = "COSH_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def EXP_talib(self):
        """

        :return:
        """
        real = ta.EXP(self.close)
        attr_name = "EXP_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def LN_talib(self):
        """

        :return:
        """
        real = ta.LN(self.close)
        attr_name = "LN_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def LOG10_talib(self):
        real = ta.LOG10(self.close)
        attr_name = "LOG_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def SIN_talib(self):
        """

        :return:
        """
        real = ta.SIN(self.close)
        attr_name = "SIN_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def SINH_talib(self):
        """

        :return:
        """
        real = ta.SINH(self.close)
        attr_name = "SINH_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def SQRT_talib(self):
        """

        :return:
        """
        real = ta.SQRT(self.close)
        attr_name = "SQRT_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def TAN_talib(self):
        """

        :return:
        """
        real = ta.TAN(self.close)
        attr_name = "TAN_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def TANH_talib(self):
        """

        :return:
        """
        real = ta.TANH(self.close)
        attr_name = "TANN_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    # -------------------------------Math Operator Functions--------------------------------#
    def ADD_talib(self):
        """
        向量加法运算
        :return:
        """
        real = ta.ADD(self.high, self.low)
        attr_name = "ADD_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def DIV_talib(self):
        """
        向量除法运算
        :return:
        """
        real = ta.DIV(self.high, self.low)
        attr_name = "DIV_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def MAX_talib(self, timeperiod=20):
        """
        周期内最大值（不满足周期返回nan）
        :return:
        """
        real = ta.MAX(self.close, timeperiod=timeperiod)
        attr_name = "MAX_talib" + str(timeperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def MAXINDEX_talib(self, timeperiod=20):
        """
        周期内最大值的索引
        :param timeperiod:
        :return:
        """
        real = ta.MAXINDEX(self.close, timeperiod=timeperiod)
        attr_name = "MAXINDEX_talib" + str(timeperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def MININDEX_talib(self, timeperiod=20):
        """
        周期内最小值得索引
        :param timeperiod:
        :return:
        """
        real = ta.MININDEX(self.close, timeperiod=timeperiod)
        attr_name = "MININDEX_talib" + str(timeperiod)
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def MULT_talib(self):
        """
        向量乘法运算
        :return:
        """
        real = ta.MULT(self.high, self.low)
        attr_name = "MULT_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def SUB_talib(self):
        """
        向量减法运算
        :return:
        """
        real = ta.SUB(self.high, self.low)
        attr_name = "SUB_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    # -------------------------------Pattern Recognition Functions 形态识别--------------------------------#
    def CDL2CROWS_talib(self):
        """
        两只乌鸦:三日K线模式，第一天长阳，第二天高开收阴，第三天再次高开继续收阴， 收盘比前一日收盘价低，预示股价下跌。
        :return:
        """
        real = ta.CDL2CROWS(self.open, self.high, self.low, self.close)
        attr_name = "CDL2CROWS_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDL3BLACKCROWS_talib(self):
        """
        三只乌鸦:三日K线模式，连续三根阴线，每日收盘价都下跌且接近最低价， 每日开盘价都在上根K线实体内，预示股价下跌。
        :return:
        """
        real = ta.CDL3BLACKCROWS(self.open, self.high, self.low, self.close)
        attr_name = "CDL3BLACKCROWS_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDL3INSIDE_talib(self):
        """
         Three Inside Up/Down 三内部上涨和下跌
        :return:
        """
        real = ta.CDL3INSIDE(self.open, self.high, self.low, self.close)
        attr_name = "CDL3INSIDE_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDL3LINESTRIKE_talib(self):
        """
        三线打击
        :return:
        """
        real = ta.CDL3LINESTRIKE(self.open, self.high, self.low, self.close)
        attr_name = "CDL3LINESTRIKE_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDL3OUTSIDE_talib(self):
        """
        三外部上涨和下跌
        :return:
        """
        real = ta.CDL3OUTSIDE(self.open, self.high, self.low, self.close)
        attr_name = "CDL3OUTSIDE_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDL3WHITESOLDIERS_talib(self):
        """
        三个白兵
        :return:
        """
        real = ta.CDL3WHITESOLDIERS(self.open, self.high, self.low, self.close)
        attr_name = "CDL3WHITESOLDIERS_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLADVANCEBLOCK_talib(self):
        """
        Advance Block 大敌当前
        :return:
        """
        real = ta.CDLADVANCEBLOCK(self.open, self.high, self.low, self.close)
        attr_name = "CDLADVANCEBLOCK_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLBELTHOLD_talib(self):
        """
        捉腰带线
        :return:
        """
        real = ta.CDLBELTHOLD(self.open, self.high, self.low, self.close)
        attr_name = "CDLBELTHOLD_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLBREAKAWAY_talib(self):
        """
        Breakaway 脱离
        :return:
        """
        real = ta.CDLBREAKAWAY(self.open, self.high, self.low, self.close)
        attr_name = "CDLBREAKAWAY_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLCLOSINGMARUBOZU_talib(self):
        """
        Closing Marubozu 收盘缺影线
        :return:
        """
        real = ta.CDLCLOSINGMARUBOZU(self.open, self.high, self.low, self.close)
        attr_name = "CDLCLOSINGMARUBOZU_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLCONCEALBABYSWALL_talib(self):
        """
        Concealing Baby Swallow 藏婴吞没
        :return:
        """
        real = ta.CDLCONCEALBABYSWALL(self.open, self.high, self.low, self.close)
        attr_name = "CDLCONCEALBABYSWALL_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLCOUNTERATTACK_talib(self):
        """
        Counterattack 反击线
        :return:
        """
        real = ta.CDLCOUNTERATTACK(self.open, self.high, self.low, self.close)
        attr_name = "CDLCOUNTERATTACK_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLDARKCLOUDCOVER_talib(self, penetration=0):
        """
        Dark Cloud Cover 乌云压顶
        :return:
        """
        real = ta.CDLDARKCLOUDCOVER(self.open, self.high, self.low, self.close, penetration=penetration)
        attr_name = "CDLDARKCLOUDCOVER_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLDOJI_talib(self):
        """
        十字线
        :return:
        """
        real = ta.CDLDOJI(self.open, self.high, self.low, self.close)
        attr_name = "CDLDOJI_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLDOJISTAR_talib(self):
        """
        十字星
        :return:
        """
        real = ta.CDLDOJISTAR(self.open, self.high, self.low, self.close)
        attr_name = "CDLDOJISTAR_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLDRAGONFLYDOJI_talib(self):
        """
        Dragonfly Doji 蜻蜓十字/T形十字
        :return:
        """
        real = ta.CDLDRAGONFLYDOJI(self.open, self.high, self.low, self.close)
        attr_name = "CDLDRAGONFLYDOJI_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLENGULFING_talib(self):
        """
        Engulfing Pattern 吞噬模式：两日K线模式，分多头吞噬和空头吞噬，以多头吞噬为例，第一日为阴线， 第二日阳线，
        第一日的开盘价和收盘价在第二日开盘价收盘价之内，但不能完全相同。
        :return:
        """
        real = ta.CDLENGULFING(self.open, self.high, self.low, self.close)
        attr_name = "CDLENGULFING_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLEVENINGDOJISTAR_talib(self, penetration=0):
        """
        Evening Doji Star 十字暮星
        :return:
        """
        real = ta.CDLEVENINGDOJISTAR(self.open, self.high, self.low, self.close, penetration=penetration)
        attr_name = "CDLEVENINGDOJISTAR_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLEVENINGSTAR_talib(self, penetration=0):
        """
        Evening Star 暮星:三日K线模式，与晨星相反，上升趋势中, 第一日阳线，第二日价格振幅较小，第三日阴线，
        预示顶部反转。
        :return:
        """
        real = ta.CDLEVENINGSTAR(self.open, self.high, self.low, self.close, penetration=penetration)
        attr_name = "CDLEVENINGSTAR_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLGAPSIDESIDEWHITE_talib(self):
        """
        Up/Down-gap side-by-side white lines 向上/下跳空并列阳线:二日K线模式，上升趋势向上跳空，下跌趋势向下跳空,
        第一日与第二日有相同开盘价，实体长度差不多，则趋势持续。
        :return:
        """
        real = ta.CDLGAPSIDESIDEWHITE(self.open, self.high, self.low, self.close)
        attr_name = "CDLGAPSIDESIDEWHITE_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLGRAVESTONEDOJI_talib(self):
        """
        Gravestone Doji 墓碑十字/倒T十字
        :return:
        """
        real = ta.CDLGRAVESTONEDOJI(self.open, self.high, self.low, self.close)
        attr_name = "CDLGRAVESTONEDOJI_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLHAMMER_talib(self):
        """
        Hammer 锤头
        :return:
        """
        real = ta.CDLHAMMER(self.open, self.high, self.low, self.close)
        attr_name = "CDLHAMMER_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLHANGINGMAN_talib(self):
        """
        Hanging Man 上吊线:一日K线模式，形状与锤子类似，处于上升趋势的顶部，预示着趋势反转。
        :return:
        """
        real = ta.CDLHANGINGMAN(self.open, self.high, self.low, self.close)
        attr_name = "CDLHANGINGMAN_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLHARAMI_talib(self):
        """
        Harami Pattern 母子线
        :return:
        """
        real = ta.CDLHARAMI(self.open, self.high, self.low, self.close)
        attr_name = "CDLHARAMI_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLHARAMICROSS_talib(self):
        """
        Harami Cross Pattern 十字孕线:二日K线模式，与母子县类似，若第二日K线是十字线，
        便称为十字孕线，预示着趋势反转。
        :return:
        """
        real = ta.CDLHARAMICROSS(self.open, self.high, self.low, self.close)
        attr_name = "CDLHARAMICROSS_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLHIGHWAVE_talib(self):
        """
        High-Wave Candle 风高浪大线
        :return:
        """
        real = ta.CDLHARAMICROSS(self.open, self.high, self.low, self.close)
        attr_name = "CDLHARAMICROSS_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLHIKKAKE_talib(self):
        """
        Hikkake Pattern 陷阱:三日K线模式，与母子类似，第二日价格在前一日实体范围内, 第三日收盘价高于前两日，反转失败，
        趋势继续。
        :return:
        """
        real = ta.CDLHIKKAKE(self.open, self.high, self.low, self.close)
        attr_name = "CDLHIKKAKE_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLHIKKAKEMOD_talib(self):
        """
        Modified Hikkake Pattern 修正陷阱:三日K线模式，与陷阱类似，上升趋势中，第三日跳空高开； 下跌趋势中，
        第三日跳空低开，反转失败，趋势继续。
        :return:
        """
        real = ta.CDLHIKKAKEMOD(self.open, self.high, self.low, self.close)
        attr_name = "CDLHIKKAKEMOD_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLHOMINGPIGEON_talib(self):
        """
        Homing Pigeon 家鸽:二日K线模式，与母子线类似，不同的的是二日K线颜色相同， 第二日最高价、
        最低价都在第一日实体之内，预示着趋势反转。
        :return:
        """
        real = ta.CDLHOMINGPIGEON(self.open, self.high, self.low, self.close)
        attr_name = "CDLHOMINGPIGEON_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLIDENTICAL3CROWS_talib(self):
        """
        CDLIDENTICAL3CROWS:Identical Three Crows 三胞胎乌鸦.
        三日K线模式，上涨趋势中，三日都为阴线，长度大致相等， 每日开盘价等于前一日收盘价，收盘价接近当日最低价，预示价格下跌
        :return:
        """
        real = ta.CDLIDENTICAL3CROWS(self.open, self.high, self.low, self.close)
        attr_name = "CDLIDENTICAL3CROWS_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLINNECK_talib(self):
        """
        In-Neck Pattern 颈内线.
        二日K线模式，下跌趋势中，第一日长阴线， 第二日开盘价较低，收盘价略高于第一日收盘价，阳线，实体较短，预示着下跌继续
        :return:
        """
        real = ta.CDLINNECK(self.open, self.high, self.low, self.close)
        attr_name = "CDLINNECK_talib"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLINVERTEDHAMMER_talib(self):
        """
        Inverted Hammer 倒锤头
        一日K线模式，上影线较长，长度为实体2倍以上， 无下影线，在下跌趋势底部，预示着趋势反转
        :return:
        """
        real = ta.CDLINVERTEDHAMMER(self.open, self.high, self.low, self.close)
        attr_name = "CDLINVERTEDHAMMER"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLKICKING_talib(self):
        """
        Kicking 反冲形态
        二日K线模式，与分离线类似，两日K线为秃线，颜色相反，存在跳空缺口
        :return:
        """
        real = ta.CDLKICKING(self.open, self.high, self.low, self.close)
        attr_name = "CDLKICKING"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLKICKINGBYLENGTH_talib(self):
        """
        Kicking - bull/bear determined by the longer marubozu 由较长缺影线决定的反冲形态
        二日K线模式，与反冲形态类似，较长缺影线决定价格的涨跌
        :return:
        """
        real = ta.CDLKICKINGBYLENGTH(self.open, self.high, self.low, self.close)
        attr_name = "CDLKICKINGBYLENGTH"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLLADDERBOTTOM_talib(self):
        """
        Ladder Bottom 梯底
        五日K线模式，下跌趋势中，前三日阴线， 开盘价与收盘价皆低于前一日开盘、收盘价，第四日倒锤头，第五日开盘价高于前一日开盘价，
        阳线，收盘价高于前几日价格振幅，预示着底部反转
        :return:
        """
        real = ta.CDLLADDERBOTTOM(self.open, self.high, self.low, self.close)
        attr_name = "CDLLADDERBOTTOM"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLLONGLEGGEDDOJI_talib(self):
        """
        Long Legged Doji 长脚十字
        一日K线模式，开盘价与收盘价相同居当日价格中部，上下影线长， 表达市场不确定性
        :return:
        """
        real = ta.CDLLONGLEGGEDDOJI(self.open, self.high, self.low, self.close)
        attr_name = "CDLLONGLEGGEDDOJI"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLLONGLINE_talib(self):
        """
        Long Line Candle 长蜡烛
        一日K线模式，K线实体长，无上下影线
        :return:
        """
        real = ta.CDLLONGLINE(self.open, self.high, self.low, self.close)
        attr_name = "CDLLONGLINE"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLMARUBOZU_talib(self):
        """
        Marubozu 光头光脚/缺影线
        一日K线模式，上下两头都没有影线的实体， 阴线预示着熊市持续或者牛市反转，阳线相反
        :return:
        """
        real = ta.CDLMARUBOZU(self.open, self.high, self.low, self.close)
        attr_name = "CDLMARUBOZU"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLMATCHINGLOW_talib(self):
        """
        Matching Low 相同低价
        二日K线模式，下跌趋势中，第一日长阴线， 第二日阴线，收盘价与前一日相同，预示底部确认，该价格为支撑位
        :return:
        """
        real = ta.CDLMATCHINGLOW(self.open, self.high, self.low, self.close)
        attr_name = "CDLMATCHINGLOW"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLMATHOLD_talib(self):
        """
        Mat Hold 铺垫
        五日K线模式，上涨趋势中，第一日阳线，第二日跳空高开影线， 第三、四日短实体影线，第五日阳线，收盘价高于前四日，预示趋势持续
        :return:
        """
        real = ta.CDLMATHOLD(self.open, self.high, self.low, self.close)
        attr_name = "CDLMATHOLD"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLMORNINGDOJISTAR_talib(self):
        """
        Morning Doji Star 十字晨星
        三日K线模式， 基本模式为晨星，第二日K线为十字星，预示底部反转
        :return:
        """
        real = ta.CDLMORNINGDOJISTAR(self.open, self.high, self.low, self.close)
        attr_name = "CDLMORNINGDOJISTAR"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLMORNINGSTAR_talib(self):
        """
        Morning Star 晨星
        三日K线模式，下跌趋势，第一日阴线， 第二日价格振幅较小，第三天阳线，预示底部反转
        :return:
        """
        real = ta.CDLMORNINGSTAR(self.open, self.high, self.low, self.close)
        attr_name = "CDLMORNINGSTAR"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLONNECK_talib(self):
        """
        On-Neck Pattern 颈上线
        二日K线模式，下跌趋势中，第一日长阴线，第二日开盘价较低， 收盘价与前一日最低价相同，阳线，实体较短，预示着延续下跌趋势
        :return:
        """
        real = ta.CDLONNECK(self.open, self.high, self.low, self.close)
        attr_name = "CDLONNECK"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLPIERCING_talib(self):
        """
        Piercing Pattern 刺透形态
        两日K线模式，下跌趋势中，第一日阴线，第二日收盘价低于前一日最低价， 收盘价处在第一日实体上部，预示着底部反转
        :return:
        """
        real = ta.CDLPIERCING(self.open, self.high, self.low, self.close)
        attr_name = "CDLPIERCING"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLRICKSHAWMAN_talib(self):
        """
        Rickshaw Man 黄包车夫
        一日K线模式，与长腿十字线类似， 若实体正好处于价格振幅中点，称为黄包车夫
        :return:
        """
        real = ta.CDLRICKSHAWMAN(self.open, self.high, self.low, self.close)
        attr_name = "CDLRICKSHAWMAN"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLRISEFALL3METHODS_talib(self):
        """
        CDLRISEFALL3METHODS 名称：Rising/Falling Three Methods 上升/下降三法
        日K线模式，以上升三法为例，上涨趋势中， 第一日长阳线，中间三日价格在第一日范围内小幅震荡， 第五日长阳线，收盘价高于第一日收盘价，
        预示股价上升
        :return:
        """
        real = ta.CDLRISEFALL3METHODS(self.open, self.high, self.low, self.close)
        attr_name = "CDLRISEFALL3METHODS"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLSEPARATINGLINES_talib(self):
        """
        Separating Lines 分离线
        二日K线模式，上涨趋势中，第一日阴线，第二日阳线， 第二日开盘价与第一日相同且为最低价，预示着趋势继续
        :return:
        """
        real = ta.CDLSEPARATINGLINES(self.open, self.high, self.low, self.close)
        attr_name = "CDLSEPARATINGLINES"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLSHOOTINGSTAR_talib(self):
        """
        Shooting Star 射击之星
        一日K线模式，上影线至少为实体长度两倍， 没有下影线，预示着股价下跌
        :return:
        """
        real = ta.CDLSHOOTINGSTAR(self.open, self.high, self.low, self.close)
        attr_name = "CDLSHOOTINGSTAR"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLSHORTLINE_talib(self):
        """
        Short Line Candle 短蜡烛
        一日K线模式，实体短，无上下影线
        :return:
        """
        real = ta.CDLSHORTLINE(self.open, self.high, self.low, self.close)
        attr_name = "CDLSHORTLINE"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLSPINNINGTOP_talib(self):
        """
        Spinning Top 纺锤
        一日K线，实体小
        :return:
        """
        real = ta.CDLSPINNINGTOP(self.open, self.high, self.low, self.close)
        attr_name = "CDLSPINNINGTOP"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLSTALLEDPATTERN_talib(self):
        """
        Stalled Pattern 停顿形态
        三日K线模式，上涨趋势中，第二日长阳线， 第三日开盘于前一日收盘价附近，短阳线，预示着上涨结束
        :return:
        """
        real = ta.CDLSTALLEDPATTERN(self.open, self.high, self.low, self.close)
        attr_name = "CDLSTALLEDPATTERN"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLSTICKSANDWICH_talib(self):
        """
        Stick Sandwich 条形三明治
        三日K线模式，第一日长阴线，第二日阳线，开盘价高于前一日收盘价， 第三日开盘价高于前两日最高价，收盘价于第一日收盘价相同
        :return:
        """
        real = ta.CDLSTICKSANDWICH(self.open, self.high, self.low, self.close)
        attr_name = "CDLSTICKSANDWICH"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLTAKURI_talib(self):
        """
        Takuri (Dragonfly Doji with very long lower shadow) 探水竿
        一日K线模式，大致与蜻蜓十字相同，下影线长度长
        :return:
        """
        real = ta.CDLTAKURI(self.open, self.high, self.low, self.close)
        attr_name = "CDLTAKURI"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLTASUKIGAP_talib(self):
        """
        Tasuki Gap 跳空并列阴阳线
        三日K线模式，分上涨和下跌，以上升为例， 前两日阳线，第二日跳空，第三日阴线，收盘价于缺口中，上升趋势持续
        :return:
        """
        real = ta.CDLTASUKIGAP(self.open, self.high, self.low, self.close)
        attr_name = "CDLTASUKIGAP"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLTHRUSTING_talib(self):
        """
        Thrusting Pattern 插入
        二日K线模式，与颈上线类似，下跌趋势中，第一日长阴线，第二日开盘价跳空， 收盘价略低于前一日实体中部，与颈上线相比实体较长，
        预示着趋势持续
        :return:
        """
        real = ta.CDLTHRUSTING(self.open, self.high, self.low, self.close)
        attr_name = "CDLTHRUSTING"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLTRISTAR_talib(self):
        """
        Tristar Pattern 三星
        三日K线模式，由三个十字组成， 第二日十字必须高于或者低于第一日和第三日，预示着反转
        :return:
        """
        real = ta.CDLTRISTAR(self.open, self.high, self.low, self.close)
        attr_name = "CDLTRISTAR"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLUNIQUE3RIVER_talib(self):
        """
        Unique 3 River 奇特三河床
        三日K线模式，下跌趋势中，第一日长阴线，第二日为锤头，最低价创新低，第三日开盘价低于第二日收盘价，收阳线，
        收盘价不高于第二日收盘价，预示着反转，第二日下影线越长可能性越大
        :return:
        """
        real = ta.CDLUNIQUE3RIVER(self.open, self.high, self.low, self.close)
        attr_name = "CDLUNIQUE3RIVER"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLUPSIDEGAP2CROWS_talib(self):
        """
        Upside Gap Two Crows 向上跳空的两只乌鸦
        三日K线模式，第一日阳线，第二日跳空以高于第一日最高价开盘， 收阴线，第三日开盘价高于第二日，收阴线，与第一日比仍有缺口
        :return:
        """
        real = ta.CDLUPSIDEGAP2CROWS(self.open, self.high, self.low, self.close)
        attr_name = "CDLUPSIDEGAP2CROWS"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    def CDLXSIDEGAP3METHODS_talib(self):
        """
        Upside/Downside Gap Three Methods 上升/下降跳空三法
        五日K线模式，以上升跳空三法为例，上涨趋势中，第一日长阳线，第二日短阳线，第三日跳空阳线，第四日阴线，
        开盘价与收盘价于前两日实体内， 第五日长阳线，收盘价高于第一日收盘价，预示股价上升
        :return:
        """
        real = ta.CDLXSIDEGAP3METHODS(self.open, self.high, self.low, self.close)
        attr_name = "CDLXSIDEGAP3METHODS"
        attr_value = real
        # self.__setattr__(attr_name, attr_value)
        return real

    @jit
    def get_all_features(self):
        """

        :return: (num of features, l)
        """
        i = 0
        l = len(self.close)
        for name in self.__allfeatures__:
            i += 1
            f = self.__getattribute__(name)()
            # print("%sth" % i, ";name:", name, ";shape:", f.shape)
            self.featuresmap = np.concatenate((self.featuresmap, f.reshape(-1, l)), axis=0)

        # TODO:这里增加其他features time lag---------------------------------------------------------------
        for i in [3,7,20,30,60]:
            f = self.BBands_talib(ndays=i)
            self.featuresmap = np.concatenate((self.featuresmap, f.reshape(-1, l)), axis=0)


        # -------------------------------------------------------------------------------------------
        a = self.featuresmap
        self.featuresmap = np.array([open, high, low, close])  # 每次都必须重置,若不重置self.featuremap下一次for会维数翻倍
        return a


if __name__ == "__main__":
    # data = pd.read_csv(r"F:\99999_day_20190308.csv")

    data = pd.read_csv(r"/home/zzw/data/rb1910_1min.csv")
    date = np.array(data['date'])
    Time = np.array(data['time'])
    open = np.array(data['open']).astype('double')
    high = np.array(data['high']).astype('double')
    low = np.array(data['low']).astype('double')
    close = np.array(data['close']).astype('double')
    volume = np.array(data['volume']).astype('double')

    # from MySqlio.mysql_api import mysqlio
    #
    # host = "localhost"
    # port = 3306
    # user = "root"
    # passwd = "318318"
    # db = "future_master"
    # symbol = 'rb1910'
    # MSL = mysqlio(host=host, port=port, user=user, passwd=passwd, db=db)
    #
    # sql = """select ts_code,trade_date,open,high,low,close,vol from {}_1min;""".format(symbol)
    # data = MSL.get_sth_from_mysql(sql=sql)
    # col_name = list(data.columns)
    #
    # date = data.index
    # open = data['open']
    # high = data['high']
    # low = data['low']
    # close = np.array(data['close'])
    # volume = np.array(data['volume'], dtype='float')

    A = features(open, high, low, close, volume)

    print(A)

    # print(A.HT_TRENDMODE_talib())
    # plot1lines(A.HT_TRENDMODE_talib())
    # plot1line(A.OBV_talib())

    # # # ma
    # ma5 = A.MA_talib(close, 5)
    # ma10 = A.MA_talib(close, 10)
    # ma20 = A.MA_talib(close, 20)
    # ma60 = A.MA_talib(close, 60)
    # MA = pd.Series(pd.Series(close).rolling(window=5, center=False).mean(), name='MA' + str(5))
    #
    # # # sma
    # sma5 = A.SMA(close, 5)
    # sma10 = A.SMA(close, 10)
    # sma20 = A.SMA(close, 20)
    # sma60 = A.SMA(close, 60)
    #
    # # ema
    # ema = A.EMA(12)
    # exc_time(A.EMA, 12)
    # exc_time(A.EMA_talib, 12)
    #
    # # ewma
    # ewma = A.EWMA(12)
