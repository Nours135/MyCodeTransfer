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
from data_connection import store_post_half

class PostCollector(RedditSpider):
    def __init__(self, post_url):
        super().__init__()
        self.post_url = post_url
        self.post_data_dict = dict()  # 存储post信息的字典
        

    def get_post_page(self):
        self.driver.get(self.post_url)
        return self
    
    def roll_down(self):
        '''滚轮向下滑动页面'''
        scroll_distance = randint(600, 900)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        return self
    
    def data_extraction(self):
        '''交替执行，向下滚动和抓取数据的操作'''
        # 向下滚动
        #while True:  # 还需要设计一个停止的逻辑
        self.success, self.total = 0, 0
        for i in range(800):
            self.roll_down()
            time.sleep(randint(3, 8)/9)
            cur_dict = self.get_page_posts()
            self.store_posts_data(cur_dict)
        print(f'本次抓取post {self.total}个，新post{self.success}个，占比{self.success/self.total:.3f}')
        return self
    

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
        print(len(posts_l))
        cur_dict = dict()

        for ele in posts_l:
            try:
                ele_content = ele.find_element(By.XPATH, './/div[@data-testid="post-container"]')
                # 获取comment URL
                comment_element = ele_content.find_element(By.XPATH, './div[3]/div[2]')  # 第2个div是获取comment
            except Exception:  # 说明不是，我需要获取的post
                continue
            
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

            # 获取时间
            time_element = ele_content.find_element(By.XPATH, './div[3]/div[1]')  # 第一个div是时间
            pattern = '\d+\s[a-zA-Z]+\sago'  # 匹配时间的字符的表达式
            matches = re.findall(pattern, time_element.text)
            if len(matches) < 1:
                continue
            
            self.post_data_dict[cur_url] = (post_id, matches[0])  # 选择第一个作为时间
            cur_dict[cur_url] = (post_id, matches[0])  # 如果加进去，也把这个加进去
            #print(post_id)
            #print(cur_url)
            #print(matches[0])

        return cur_dict  # 我裂开了，每次都穿，都传

    def store_posts_data(self, cur_dict):
        '''将之前获取到的所有post都存入数据库'''
        

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
            create_time = int(current_time.timestamp()) # 今天
            current_time = int(current_time.timestamp()) # 转化为时间戳
            
            res = store_post_half((post_id, create_time, current_time, comment_url),
                                  db=self.db,
                                  cursor=self.cursor)
            if res == 1:
                self.success += 1
            self.total += 1
        print(f'本次抓取post {self.total}个，新post{self.success}个，占比{self.success/self.total:.3f}')
        
        





if __name__ == '__main__':
    # post_url = 'https://www.reddit.com/r/science/'
    post_url = 'https://www.reddit.com/r/science/hot/'
    driver = PostCollector(post_url)
    driver.log_in().get_post_page().data_extraction()