# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 03:50:38 2017

@author: bladez
"""
#%%some import works
import pandas as pd
import matplotlib.pyplot as plt

#%% data importing

data = pd.read_excel('d:\dumps\999999_1v2.xlsx')
data0 = data.drop(0,axis = 0)
del data
Date = pd.Series(data0.iloc[:,0],name = 'Date')
Open = pd.Series(data0.iloc[:,1],name = 'Open')
High = pd.Series(data0.iloc[:,2],name = 'High')
Low  = pd.Series(data0.iloc[:,3],name = 'Low')
Close= pd.Series(data0.iloc[:,4],name = 'Close')
Price = Close.copy()

#%% the feature
def DAMA( Price, len=10, fastlen=4, slowlen=23, c1=0.003 ):
    
    #AMA diff of adapted moving average
    ama1=AMA(Price, len, fastlen, slowlen)
    l=length(Price)
    dama=zeros(l,1)
    dama(1:len-1)=0
    ama2=ama1
    ama2(1)=[]
    ama3=[ama2;0]#这个时候ama3比ama2少一个数
    dama0=ama3-ama1                       
    dama0(end)=[]
    dama=[0;dama0]

for i=1:l
    if(dama(i)*dama(i)<=c1)
        dama(i)=0;
    end
end