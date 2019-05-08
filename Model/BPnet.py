
import csvdata

# some import works
import pandas as pd
import numpy as np

import torch



from feature.features import features


# Generate dummy data
datapath = csvdata.csvdatapaths[0]  # 输入需要训练的文件
data = pd.read_csv(datapath)  # 载入csv文件
date = np.array(data['date'])
Time = np.array(data['time'])
open = np.array(data['open'])
high = np.array(data['high'])
low = np.array(data['low'])
close = np.array(data['close'])
volume = np.array(data['volume'])

Fs = features(open, high, low, close, volume)  # 这里有狠多特征,取需要的用


x = Fs.close.astype('float32')
len_x = len(x)
y = (np.sign(Fs.close[1:] - Fs.close[:-1])).astype("int")
y = np.insert(y, 0, 0)  # 在0位插入一个nan,使其长度与x相等


# from sklearn.preprocessing import LabelBinarizer
# lb = LabelBinarizer()
# lb.fit([1, 0, -1])
# y = lb.transform(y_)  # 转换成3列



x_train_endpoint = int(len_x * 0.7)  # 向下取整
x_val_endpoint_ = int(len_x * 0.15)  # 向下取整


x_train = x[:x_train_endpoint]
y_train = y[:x_train_endpoint]
# x_val = x[x_train_endpoint: x_val_endpoint_]
# y_val = y[x_train_endpoint: x_val_endpoint_]
x_test = x[x_train_endpoint:]
y_test = y[x_train_endpoint:]



#
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

class MyDataset(Dataset):
    def __init__(self, x, y, window=5, transform=None, target_transform = None):

        xs = []
        for i in range(len(x)-window):
            x_ = x[i:i+window]
            label_ = y[i+window-1]
            xs.append((x_, label_))

        self.xs = xs  # 最主要就是要生成这个list， 然后DataLoader中给index，通过getitem读取图片数据
        self.transform = transform
        self.target_transform = target_transform

    def __getitem__(self, index):
        x, label = self.xs[index]
        if self.transform is not None:
            print("self.transform is not None:", self.transform is not None)   # 在这里做transform，转为tensor等等

        return x, label

    def __len__(self):
        return len(self.xs)

train_data = MyDataset(x=x_train, y=y_train, window=100)
test_data = MyDataset(x=x_test, y=y_test, window=100)

train_bs = 100
test_bs = 100
train_loader = DataLoader(dataset=train_data, batch_size=train_bs)
test_loader = DataLoader(dataset=test_data, batch_size=test_bs)



import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(100, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 3)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

net = Net()
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
net.to(device)
criterion = nn.SoftMarginLoss()
# optimizer = optim.Adam(model.parameters(), lr=0.001)
lr_init = 0.001
optimizer = optim.SGD(net.parameters(), lr=lr_init, momentum=0.9, dampening=0.1)    # 选择优化器
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=50, gamma=0.1)     # 设置学习率下降策略


for epoch in range(10):  # loop over the dataset multiple times

    running_loss = 0.0
    for i, data in enumerate(train_loader, 0):
        # get the inputs
        inputs, labels = data
        inputs, labels = inputs.to(device), labels.to(device)
        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # print statistics
        running_loss += loss.item()
        if i % 2000 == 1999:    # print every 2000 mini-batches
            print('[%d, %5d] loss: %.3f' %
                  (epoch + 1, i + 1, running_loss / 2000))
            running_loss = 0.0


print('Finished Training')
