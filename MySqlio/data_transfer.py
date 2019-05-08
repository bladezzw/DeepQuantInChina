# -*- coding:utf-8 -*-
import tushare as ts

def df2csv(df,path_name):
    """
    保存为CSV文件
    :param df:
    :param path_name: path_name='c:/day/000875.csv'
    :return:
    """
    df.to_csv(path_name)

def df2excel(df,path_name):
    """
    保存为excel文件
    :param df:
    :param path_name: 'c:/day/000875.xlsx'
    :return:
    """
    df.to_excel(path_name)

def df2json(df,path_name,orient):
    """
    保存为json格式
    :param df:
    :param path_name: 'c:/day/000875.json',orient='records')
    :Param orient:json格式顺序，包括columns，records，index，split，values，默认为columns
    :return:
    """
    df.to_json(path_name,orient)

if __name__ == '__main__':
    print("data_transfer_module".center(20,'-'))
