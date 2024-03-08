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
        },{
            'mail':'No_Efficiency6713', 'pwd': 'yskt2333.'
        },{
            'mail':'dismerit_sdasa', 'pwd': 'n.nvFh-gZ3SVR!G'  # qq mail注册的
        }
        
    ]
    
    log_in_url = 'https://www.reddit.com/login/'

    def __init__(self):
        opt = Options()
         #   opt.add_argument('--headless')
        # opt.add_argument("--disable-gpu")
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

        # 将login中，获取网页和邮件密码的东西，都放到前面，没必要重复
        account_dict = self.reddit_account[randint(0, len(self.reddit_account) - 1)]
        self.mail = account_dict['mail']
        self.pwd = account_dict['pwd']
        self.driver.get(self.log_in_url)
        try:
            self.log_in2()
        except Exception:
            self.log_in()


    def log_in(self):
        self.driver.get(self.log_in_url)
        # 输入账号密码
        time.sleep(randint(3, 8)/7)
        log_in_forum_xpath = '//*[@id="loginUsername"]'
        WebDriverWait(self.driver, 10, 1).until(
                          EC.presence_of_element_located((By.XPATH, log_in_forum_xpath))
                          )
        mail_input_xpath = '//*[@id="loginUsername"]'
        pwd_input_xpath = '//*[@id="loginPassword"]'
        mail_element = self.driver.find_element(By.XPATH, mail_input_xpath)
        pwd_element = self.driver.find_element(By.XPATH, pwd_input_xpath)
        mail_element.send_keys(self.mail)
        time.sleep(randint(3, 8)/7)
        pwd_element.send_keys(self.pwd)
        # 点击登录
        log_in_click_xpath = '/html/body/div/main/div[1]/div/div[2]/form/fieldset[5]/button'
        log_in_click_element = self.driver.find_element(By.XPATH, log_in_click_xpath)
        time.sleep(randint(3, 8)/7)
        ActionChains(self.driver).move_to_element(log_in_click_element).pause(randint(3, 8)/7).click(log_in_click_element).perform()
        time.sleep(randint(6, 8)/2)
        return self
    
    def log_in2(self):

        # 输入账号密码
        time.sleep(randint(3, 8)/7)
        log_in_forum_xpath = '//*[@id="login-username"]'
        WebDriverWait(self.driver, 10, 1).until(
                          EC.presence_of_element_located((By.XPATH, log_in_forum_xpath))
                          )
        mail_input_xpath = '//*[@id="login-username"]'
        pwd_input_xpath = '//*[@id="login-password"]'
        mail_element = self.driver.find_element(By.XPATH, mail_input_xpath)
        pwd_element = self.driver.find_element(By.XPATH, pwd_input_xpath)
        mail_element.send_keys(self.mail)
        time.sleep(randint(3, 8)/7)
        pwd_element.send_keys(self.pwd)
        # 点击登录

        '''log_in_click_xpath = '//*[@id="login"]/faceplate-tabpanel/auth-flow-modal[1]/div[2]/faceplate-tracker'
        WebDriverWait(self.driver, 10, 1).until(
                          EC.presence_of_element_located((By.LINK_TEXT, log_in_click_xpath))
                          )
        log_in_click_element = self.driver.find_element(By.XPATH, log_in_click_xpath)
        time.sleep(randint(3, 8)/7)
        ActionChains(self.driver).move_to_element(log_in_click_element).pause(randint(3, 8)/7).click(log_in_click_element).perform()'''
        time.sleep(randint(6, 8)/2)
        return self


if __name__ == '__main__':
    t = RedditSpider()