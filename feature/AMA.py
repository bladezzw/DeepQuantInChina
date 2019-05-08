# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 03:54:18 2017

@author: Administrator
"""
#%%some import works
import pandas as pd
import numpy as np
import features as ft
import matplotlib.pyplot as plt

#%% data importing

data = pd.read_excel('d:\dumps\999999_1v2.xlsx')

Date = pd.Series(data.iloc[:,0],name = 'Date')
Open = pd.Series(data.iloc[:,1],name = 'Open')
High = pd.Series(data.iloc[:,2],name = 'High')
Low  = pd.Series(data.iloc[:,3],name = 'Low')
Close= pd.Series(data.iloc[:,4],name = 'Close')
Price = Close.copy()
#%% the feature
def AMA(Price, length=10, fastlen=4, slowlen=23):

    # 指定AMA系数
    fast = 4./(fastlen + 1)
    slow = 2./(slowlen + 1)
    # 计算EMAvalue
    DMAvalue=np.zeros(len(Price))
    DMAvalue[0:length-1]=Price[0:length-1].copy()
    AMAvalue = np.zeros(len(Price))
    AMAvalue[0:length-1] = Price[0:length-1]
    
    direction = abs( Price-Price.shift(length))
    b = abs(Price - Price.shift(1))
    for i in range(length,len(Price)):

        volatility = sum( b[i-length+1:i+1] )
        #Efficiency_Ratio
        Er = direction[i]/volatility
        smooth = Er*(fast-slow) + slow
        c = smooth*smooth
        DMAvalue[i] = DMAvalue[i-1] + c*(Price[i]-DMAvalue[i-1])
        
        
    AMAvalue=ft.EWMA(DMAvalue,2)
    
    return AMAvalue