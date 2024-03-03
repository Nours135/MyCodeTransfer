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
from datetime import datetime


class PostCollector(RedditSpider):
    def __init__(self):
        super().__init__()
    
    def roll_down():
        '''滚轮向下滑动页面'''
        pass
