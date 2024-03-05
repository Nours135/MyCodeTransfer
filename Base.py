# 基类

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


from utils import get_proxy
import time 
from random import randint
from tqdm import tqdm
from datetime import datetime

from data_connection import get_db

class RedditSpider():
    reddit_account = [
        {
            'mail':' Nournours135', 'pwd': 'KLWDriverbone135'
        }, {
            'mail':'mangorice7890', 'pwd': 'qjc12011013@'
        }
    ]
    
    log_in_url = 'https://www.reddit.com/login/'

    def __init__(self):
        opt = Options()
         #   opt.add_argument('--headless')
        opt.add_argument("--disable-gpu")
        opt.add_experimental_option('excludeSwitches', ['enable-automation'])
        opt.add_experimental_option('useAutomationExtension', False)   #把webdriver的属性调成false
        opt.add_argument(f'--proxy-server={get_proxy()}')
        self.driver = Chrome(options=opt)

        self.driver.execute_cdp_cmd(   # 似乎也是防止反爬检测的
            'Page.addScriptToEvaluateOnNewDocument',
            {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'}
        )
        self.db = get_db()
        self.cursor = self.db.cursor()


    def log_in(self):
        account_dict = self.reddit_account[randint(0, len(self.reddit_account) - 1)]
        mail = account_dict['mail']
        pwd = account_dict['pwd']

        self.driver.get(self.log_in_url)
        # 输入账号密码
        time.sleep(randint(3, 8)/7)
        log_in_forum_xpath = '//*[@id="loginUsername"]'
        WebDriverWait(self.driver, 360, 1).until(
                          EC.presence_of_element_located((By.XPATH, log_in_forum_xpath))
                          )
        mail_input_xpath = '//*[@id="loginUsername"]'
        pwd_input_xpath = '//*[@id="loginPassword"]'
        mail_element = self.driver.find_element(By.XPATH, mail_input_xpath)
        pwd_element = self.driver.find_element(By.XPATH, pwd_input_xpath)
        mail_element.send_keys(mail)
        time.sleep(randint(3, 8)/7)
        pwd_element.send_keys(pwd)
        # 点击登录
        log_in_click_xpath = '/html/body/div/main/div[1]/div/div[2]/form/fieldset[5]/button'
        log_in_click_element = self.driver.find_element(By.XPATH, log_in_click_xpath)
        time.sleep(randint(3, 8)/7)
        ActionChains(self.driver).move_to_element(log_in_click_element).pause(randint(3, 8)/7).click(log_in_click_element).perform()
        time.sleep(randint(6, 8)/2)
        return self