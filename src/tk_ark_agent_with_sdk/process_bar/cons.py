from datetime import datetime
class ProcessBar(object):
    def __init__(self,total:int,desc:str):
        self.total = total
        self.first_time = None
        self.latest_time = None
        self.last_time = None
        self.desc = desc
        self.count = 0
        self.total_time = 0
        self.latest_time_cost = 0
    
    def start(self):
        self.first_time = datetime.now()
    def update_bar(self,current:int):
        self.latest_time = datetime.now()
        if self.last_time is None:
            self.latest_time_cost = self.latest_time - self.first_time
            self.total_time += self.latest_time_cost.seconds
            self.last_time = self.latest_time
        else:
            self.latest_time_cost = self.latest_time - self.last_time
            self.total_time += self.latest_time_cost.seconds
        self.count += current
        print(f'程序执行进度:{self.count}/{self.total}，{self.desc}，最近一个项目耗时:{self.latest_time_cost}，总耗时:{self.total_time},平均每个项目耗时:{self.total_time/self.count}',end='\r')
        
        

