import numpy as np
import talib as ta
import pandas as pd
from features import features

class feature(features):

    def set_attr(self, func, *args, **kwargs):#给实例加上属性
        def wrapper(*args, **kwargs):
            attr_name = func.__name__ + str(*args,**kwargs)
            print(attr_name)
            attr_value = func(*args, **kwargs)
            self.__setattr__(attr_name, attr_value)
        return wrapper(*args, **kwargs)


    def AROONOSC_talib(self, ndays):
        """
        :param ndays:
        :return:
        """
        real = ta.AROONOSC(self.high, self.low, timeperiod=ndays)
        return real




if __name__ == "__main__":
    data = pd.read_csv(r"/media/zzw/File/99999_day_20190308.csv")
    col_name = list(data.columns)
    date = np.array(data['date'])
    open = np.array(data['open'])
    high = np.array(data['high'])
    low = np.array(data['low'])
    close = np.array(data['close'])
    volume = np.array(data['volume'])

    A = feature(open, high, low, close, volume)

    A.set_attr(A.AROONOSC_talib,10)

    print('1')