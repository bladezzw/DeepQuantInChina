# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 21:55:54 2018

@author: bladezzw
"""

import pandas as pd

def get_data_from_mysql(name):
    d = pd.read_csv('/home/bladezzw/data/'+name+'.day.csv')
    return d
    