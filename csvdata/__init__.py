import os
datadir = os.path.dirname(__file__)
list = os.listdir(datadir) #列出文件夹下所有的目录与文件
csvdatapaths = []
for i in range(0, len(list)):
    path_ = os.path.join(datadir, list[i])
    if path_[-3:] == 'csv':
        csvdatapaths.append(path_)

print("csvdatapath:", csvdatapaths)  # 如果载入这个包,就打印此文件夹下面的csv文件路径.方便调用