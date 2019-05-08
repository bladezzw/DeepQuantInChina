"""
python子进程中不支持队列, 不知道是否有bug,所以自己写了一个队列
"""

class myqueue:

    def __init__(self):
        self.list_ = []

    def empty(self):
        return self.list_ == []

    def put(self, item):
        self.list_.append(item)

    def get(self):
        item = self.list_[0]
        self.list_.pop(0)
        return item

    def __len__(self):
        return self.list_.__len__()



if __name__ == "__main__":
    event=myqueue()
    event.put('a')
    from backtesting.event import EventMarket
    event.put(EventMarket())
    event.__len__()

    event.get()



    event.empty()

