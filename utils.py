def get_proxy():
    '''format: str'''
    fpath = 'proxy.txt'
    with open(fpath, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    return lines[0].strip()

class MyQueue():
    '''自动队列，新加入的会把后面的寄出去'''
    def __init__(self, l):
        self._lenth = l
        self._data = []
    
    def __len__(self):
        return len(self._data)
    
    def append(self, item):
        if len(self) < self._lenth:  # 未装满，则直接末尾加入
            self._data.append(item)
        else:
            self._data.pop(0) # 把第一个pop掉
            self._data.append(item)
    
    def check_same(self, item):
        '''判断item是否和data内所有的都一样'''
        if len(self) < self._lenth:  # 未装满，则直接末尾加入
            return False
        
        for obj in self._data:
            if obj != item:
                return False
        return True

    def __str__(self):
        return str(self._data)
    def __repr__(self) -> str:
        return str(self._data)

