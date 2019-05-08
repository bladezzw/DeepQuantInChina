# -*- coding: utf-8 -*-
"""
Created on Mon Mar 06 07:57:27 2017

@author: bladez
"""

"""
没试过
import os
import sys
def search(path, word):
    for fname in os.listdir(path):
        print fname
        fp = os.path.join(path, fname)
        if os.path.isfile(fp):
            with open(fp) as f:
                for line in f:
                    if word in line:
                        print fp
                        break
        elif os.path.isdir(fp):
            search(fp, word)
search(sys.argv[1], sys.argv[2])
"""
###不包含子目录
import glob
def findfile(path= '/media/bladez/软件/new_gxzq_v6/vipdoc/ds/minline/',keyname ='RM' ,style = 1):
    #style = 0 means: '*{0}*';
    #style = 1 means: '{0}*';
    #style = 2 means: '*{0}';
    if style == 0:
        strfname = path + '{0}*'.format(keyname)
    elif style == 1:
        strfname = path + '*{0}*'.format(keyname)
    elif style == 2:
        strfname = path + '*{0}'.format(keyname)
    tempname = []
    for filename in glob.glob(strfname):
        tempname.append(filename)
        #print filename
    return tempname
###包含子目录
"""
#这个没试过
import os
import fnmatch
def iterfindfiles(path, fnexp):
    for root, dirs, files in os.walk(path):
        for filename in fnmatch.filter(files, fnexp):
            yield os.path.join(root, filename) 
for filename in iterfindfiles(r"f:/py", "*.exe"):
    print filename
"""
###



import os
def day2csv_data(dirname,fname,targetDir):
    ofile = open(dirname+os.sep+fname,'rb')
    ofile = open(path,'rb')
    buf = ofile.read()
    ofile.close()
    
    ifile = open('/home/bladez/dumps/'+fname+'.csv','w')
    num = len(buf)
    no = num/32
    b = 0
    e = 32
    line = ''
    linename = str('date')+','+str('open')+','+str('high')+','+str('low')+','+str('close')+','+str('amount')+','+str('vol')+','+str('str07')+''+'\n'
    linename = 'date,open,high,low,close,amount,vol,str07 '+'\n'
    #print line
    ifile.write(linename)
    for i in xrange(no):
        a = unpack('IIIIIfII',buf[b:e])
        line = str(a[0])+','+str(a[1]/100.0)+','+str(a[2]/100.0)+','+str(a[4]/100.0)+'.'+str(a[5]/10.0)+','+str(a[6])+','+str(a[7])+''+'\n'
        # print line
        ifile.write(line)
        b = b+32
        e = e+32
    
    ifile.close()











def get1minds_future(keyname='RML8',path = '/media/bladez/软件/new_gxzq_v6/vipdoc/ds/minline/' ):
    
    #%   pref is  
    #%   Examples:
    #%             %Get all records and a list of the field names from a .minline file.
    #%           data=get1minds(''/media/bladez/软件/new_gxzq_v6/vipdoc/ds/minline','28#','RML9')
    #%   先用资源管理器搜索，找到想要的数据，然后按次序填写函数
    
    fname=findfile(path,keyname)
    f1 = open(fname,'r')
    f1 = open('/media/bladez/软件/new_gxzq_v6/vipdoc/ds/minline/28#RML8.lc1','r')
 
    d=dir(fname);
    n=d.bytes/32;
    data=fread(f1,[8,n],'uint32');
    d1=mod(data(1,:),65536);
    t=fix(data(1,:)/65536);
          
    dt=datenum(fix(d1/2048)+2004,fix(mod(d1,2048)/100),mod(mod(d1,2048),100),fix(t/60),mod(t,60),0);
              
    vol=data(7,:);
    frewind(f1);
    data=fread(f1,[8,n],'float=>double');
    data(1,:)=dt;data(7,:)=vol;
        
    date=data(1,:)';
    close=data(5,:)';
    vol  =data(7,:)';
    
              
    #%min5=fints(data(1,:),data((2:7),:)',{'open','high','low','close','amount','volume'},1,strcat(stockNo,'分钟线'));
    #%min5=data';
    return date,close,vol


function min5 =get5min(datapath,market,stockNo)
%   market is 'sh' or 'sz'
%   Examples:
%             %Get all records and a list of the field names from a .day file.
%           [fis]=get5min('F:\new_gxzq_v6','sz','000001')
%

fname=strcat(datapath,'\vipdoc\',market,'\fzline\',market,stockNo,'.lc5');
f1=fopen(fname);
d=dir(fname);
n=d.bytes/32;
data=fread(f1,[8,n],'uint32');
d1=mod(data(1,:),65536);t=fix(data(1,:)/65536);



dt=datenum(fix(d1/2048)+2004,fix(mod(d1,2048)/100),mod(mod(d1,2048),100),fix(t/60),mod(t,60),0);
 
vol=data(7,:);
frewind(f1);
data=fread(f1,[8,n],'float=>double');
data(1,:)=dt;data(7,:)=vol;

date=data(1,:);
close=data(5,:);

min5=[date;close]';
%min5=fints(data(1,:),data((2:7),:)',{'open','high','low','close','amount','volume'},1,strcat(stockNo,'ｷﾖﾖﾓﾏﾟ'));
%min5=data';
end



function [days]=getday(datapath,market,stockcode)
%
%
%      market is 'sh' or 'sz'
%      stockNo is 6 chars that is the stock Number like '000001'
% 
% datapath = 'F:\new_gxzq_v6'
% market = 'sh'
% stockcode = '600665'
%
%      Example:
%          %Get all records and a list of the field names from a .day file.
%          
%          [fts]=getday('F:\new_gxzq_v6','sz','000001')


fname=strcat(datapath,'\vipdoc\',market,'\lday\',market,stockcode,'.day');
f1=fopen(fname);
d=dir(fname);
n=d.bytes/32;
data=fread(f1,[8,n],'uint32');
frewind(f1);
fseek(f1,20,-1);
data(6,:)=fread(f1,n,'float=>float',28);
data(2:5,:)=data(2:5,:)/100;
data(1,:)=datenum(fix(data(1,:)/10000),fix(mod(data(1,:)/100,100)),mod(data(1,:),100));

date=data(1,:);
open =data(2,:);
high =data(3,:);
low  =data(4,:);
close=data(5,:);
vol  =data(6,:);
days=[date;open;high;low;close;vol]';
%days=fints(data(1,:)',data([2:7],:)',{'open','high','low','close','amount','volume'},1,strat(stockNo,'ﾈﾕﾏﾟ'));
end

