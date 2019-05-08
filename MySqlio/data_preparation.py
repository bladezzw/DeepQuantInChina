# -*- coding:utf-8 -*-
import pandas as pd
import time
import numpy as np
#data_preparation数据预处理

def none2str_0(df):
    """
    change nan to 'replace_str' and 'none' to 0
    :param data: DataFrame
    :replace_str: str char that you wanna to replace none
    This will be involved into a class ('data_preparation') in the future
    """
    for col in df.columns:
        
        try:
            if str(type(df[col].iloc[0]))=="<class 'numpy.float64'>" or str(type(df[col].iloc[0]))=="<class 'NoneType'>":
                boo_value = pd.isnull(df[col])
                df[col][boo_value] = 0
            if str(type(df[col].iloc[0]))=="<class 'str'>":
                boo_value = pd.isnull(df[col])
                df[col][boo_value] = 'Null'
            
        except Exception as ee:
            print(ee)
        
    return df

def create_pd_Series(values,length_=10,name=''):
    #如果数据就是一个单一的变量，如数字4，那么Series将重复
    #这个变量：
    pd_S = pd.Series(values, index=range(length_),name=name)
    return pd_S


if __name__ == '__main__':
    print("data_preparation_module".center(20,'-'))

    pd = create_pd_Series(values=time.strftime('%Y%m%d'),length_= 10,name='date')
    print(pd)
    

            
        
        
