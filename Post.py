# 获取post的部分就在这了

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from Base import RedditSpider


import time 
from random import randint
from tqdm import tqdm
from datetime import datetime, timedelta

import re
from data_connection import store_post_half, get_db
from utils import MyQueue
import os

class PostCollector(RedditSpider):
    def __init__(self):
        super().__init__()
        #self.post_url = post_url
        self.post_data_dict = dict()  # 存储post信息的字典
        #self.last_connection = int(datetime.timestamp())        

    def get_post_page(self, post_url):
        self.driver.get(post_url)
        return self
    
    def roll_down(self):
        '''滚轮向下滑动页面'''
        scroll_distance = randint(600, 1200)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        return self
    
    def data_extraction(self):
        '''交替执行，向下滚动和抓取数据的操作'''
        # 向下滚动
        #while True:  # 还需要设计一个停止的逻辑
        self.success, self.total = 0, 0
        check_hash_queue = MyQueue(12)  # 如果 12 次下拉后，获取的 cur_dict 的hash值一致，则自动停止
        for i in range(800):
            self.roll_down()
            time.sleep(randint(3, 8)/3)
            posts_obj_str, cur_dict = self.get_page_posts()
            # 反正这个就是判断的indicator，可以加一个
            if check_hash_queue.check_same(posts_obj_str):  # 就break就好了，中断爬取
                break
            check_hash_queue.append(posts_obj_str)

            self.store_posts_data(cur_dict)
        print(f'本次抓取post {self.total}个，新post{self.success}个，占比{self.success/(self.total + 0.01):.3f}')
        return self.success/(self.total + 0.01)
    

    def get_posts_container_element(self):
        '''获取，posts的容器的element'''
                            #   //*[@id="AppRouter-main-content"]/div/div/div[2]/div[4]/div[1]/div[5]
        post_container_xpath = '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[4]/div[1]/div[5]'
        try:
            WebDriverWait(self.driver, 10, 1).until(
                          EC.presence_of_element_located((By.XPATH, post_container_xpath))
                          )
        except Exception:
            # 超时，换令一个就好了，这是因为有广告会这样TT
            post_container_xpath = ''
        res = self.driver.find_element(By.XPATH, post_container_xpath)
        return res
    

    def get_page_posts(self):
        '''抓取所有post信息'''
        post_container = self.get_posts_container_element()   # 稍微封装一下
        posts_l = post_container.find_elements(By.XPATH, './div') # 下面所有的div
        posts_obj_str = str(posts_l)
        print(len(posts_l))
        cur_dict = dict()

        for ele in posts_l:
            try:
                ele_content = ele.find_element(By.XPATH, './/div[@data-testid="post-container"]')
                # 获取comment URL
                comment_element = ele_content.find_element(By.XPATH, './div[3]/div[2]')  # 第2个div是获取comment
            except Exception:  # 说明不是，我需要获取的post
                try:
                    ele_content = ele.find_element(By.XPATH, './/div[@data-testid="post-container"]')
                    # print([e.text for e in ele_content.find_elements(By.XPATH, './*')])
                    comment_element = ele_content.find_element(By.XPATH, './div[2]/article/div[1]')  # 如果是 另一个作为搜索的界面，需要这个
                except Exception:
                    continue  # 还不行就算了

            post_id = ele_content.get_attribute("id")
            link_eles = comment_element.find_elements(By.XPATH, './/a')
            for link_ele in link_eles:
                cur_url = link_ele.get_attribute("href")
                if 'r/science/comments' in cur_url:
                    break
            else:
                continue  # 循环正常退出，没有匹配到网页

            if cur_url in self.post_data_dict:  # 该post已经被记录了
                continue
            
            # 获取时间  # 另一个 './div[2]/article/div[1]/div[1]'
            try:
                time_element = ele_content.find_element(By.XPATH, './div[3]/div[1]')  # 第一个div是时间
            except Exception:
                try:
                    time_element = ele_content.find_element(By.XPATH, './div[2]/article/div[1]/div[1]')    # 兼容令一个版本代码
                except Exception:
                    continue 
            pattern = '\d+\s[a-zA-Z]+\sago'  # 匹配时间的字符的表达式
            matches = re.findall(pattern, time_element.text)
            if len(matches) < 1:
                continue
            # print(matches[0])
            
            self.post_data_dict[cur_url] = (post_id, matches[0])  # 选择第一个作为时间
            cur_dict[cur_url] = (post_id, matches[0])  # 如果加进去，也把这个加进去
            #print(post_id)
            #print(cur_url)
            #print(matches[0])

        return posts_obj_str, cur_dict  # 我裂开了，每次都穿，都传

    def store_posts_data(self, cur_dict):
        '''将之前获取到的所有post都存入数据库'''
        if len(list(cur_dict.items())) == 0:
            return
        if not self.db.ping(reconnect=True):    # 时间比较长再更新connection
            self.db = get_db()
            self.cursor = self.db.cursor()  # 应该是timeout了，不是网络的问题
            
        for key, values in tqdm(cur_dict.items(), desc='传输post 数据'):
            comment_url = key
            post_id = values[0]
            create_time = values[1]
            current_time = datetime.today()
            if 'day' in create_time:
                delta_values = int(create_time.split(' ')[0])  # 取出差值的数字
                create_time = current_time - timedelta(days=delta_values)
            elif 'month' in create_time:
                delta_values = int(create_time.split(' ')[0])  # 取出差值的数字
                create_time = current_time - timedelta(days=delta_values * 30)
            elif 'year' in create_time:
                delta_values = int(create_time.split(' ')[0])  # 取出差值的数字
                create_time = current_time - timedelta(days=delta_values * 365)
            else:
                create_time = datetime.today()  # 第一阶段的统计只精确到天
            create_time = int(create_time.timestamp()) # aaaaa 我乱改代码我忏悔
            current_time = int(current_time.timestamp()) # 转化为时间戳
            
            res = store_post_half((post_id, create_time, current_time, comment_url),
                                  db=self.db,
                                  cursor=self.cursor)
            if res == 1:
                self.success += 1
            self.total += 1
        print(f'本次抓取post {self.total}个，新post{self.success}个，占比{self.success/self.total:.3f}')
        
        





if __name__ == '__main__':
    # 目前所有可以抓取的页面
    # post_url = 'https://www.reddit.com/r/science/'
    post_url = 'https://www.reddit.com/r/science/hot/'
    post_url = 'https://www.reddit.com/r/science/new/'
    post_url = 'https://www.reddit.com/r/science/top/'   # 有很多 250 
    # post_url = 'https://www.reddit.com/r/science/top/?t=day' # 很快就没了
    # post_url = 'https://www.reddit.com/r/science/top/?t=week'  # 也没多少，好像在top里被包括了
    # post_url = 'https://www.reddit.com/r/science/top/?t=month'  # 还是基本冲复了
    # post_url = 'https://www.reddit.com/r/science/top/?t=year'  # 这里会有比较多新的
    # post_url = 'https://www.reddit.com/r/science/top/?t=all'  # 很多新的
    # post_url = 'https://www.reddit.com/r/science/rising/'

    post_url = 'https://www.reddit.com/r/science/?f=flair_name%3A%22Psychology%22'
    post_url = 'https://www.reddit.com/r/science/?f=flair_name%3A%22Social%20Science%22'
    post_url = 'https://www.reddit.com/r/science/?f=flair_name%3A%22Health%22'  
    post_url = r'https://www.reddit.com/r/science/?f=flair_name%3A%22Environment%22'
    post_url = 'https://www.reddit.com/r/science/?f=flair_name%3A%22Medicine%22'  
    post_url = 'https://www.reddit.com/r/science/?f=flair_name%3A%22Biology%22'
    post_url = 'https://www.reddit.com/r/science/rising/'

    post_urls = [  # 后面把这部分的逻辑改为，随机选择url，然后循环爬取
        'https://www.reddit.com/r/science/hot/',
        'https://www.reddit.com/r/science/new/',
        'https://www.reddit.com/r/science/top/',
        # 'https://www.reddit.com/r/science/top/?t=year',  # 感觉这两个，基本不会更新了
        # 'https://www.reddit.com/r/science/top/?t=all',
        'https://www.reddit.com/r/science/top/?t=week',
        'https://www.reddit.com/r/science/rising/'
    ]

    # 后面有空需要加一下自动检测停止的逻辑了
    driver = PostCollector()
    driver.get_post_page(post_url).data_extraction()

    # 新代码逻辑
    # driver = PostCollector()
    # driver.log_in()
    while True:
        cur_url = post_urls[randint(0, len(post_urls) - 1)]
        stats = driver.get_post_page(cur_url).data_extraction()

        # 接下来记录下，这个页面的获取的url的占比
        stats_f = 'post_page_stats.txt'
        if os.path.exists(stats_f):
            fp = open(stats_f, 'w', encoding='utf-8')
        else:
            fp = open(stats_f, 'a', encoding='utf-8')
        fp.write(f'{cur_url} | {round(stats, 2)}')
        fp.close()

