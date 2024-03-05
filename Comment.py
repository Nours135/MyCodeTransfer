# Comment Spider
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
from data_connection import store_post_full, get_task, check_queue, get_db
import json

class CommentSpider(RedditSpider):
    mother_url = 'https://www.reddit.com'
    def __init__(self):
        super().__init__()
        

    def __call__(self, comment_url):
        '''以一个页面为周期进行爬取'''
        self.comment_url = comment_url
        # self.comment_full_url = self.mother_url + comment_url
        self.get_comment_page().extract_post_data()  # 获取post信息
        self.click_more_reply_recursively().click_expand().extract_all_comments()  # 获取comment信息
        self.restore_all_extracted_data()

    def restore_all_extracted_data(self):
        '''在所有数据抓取后，存储数据'''
        if not self.db.ping(reconnect=True):
            self.db = get_db()
            self.cursor = self.db.cursor()  # 应该是timeout了，不是网络的问题

        values = (
            json.dumps(self.post_data_json), json.dumps(self.comment_data_l), self.article_origin_link, int(datetime.today().timestamp()), self.comment_url
        )
        
        res = store_post_full(values, self.db, self.cursor)
        if res != 1:
            print('这个页面存储进入数据库出错，我也不知道咋办')


    def get_comment_page(self):
        self.driver.get(self.comment_url)
        return self


    def click_more_reply(self, click=True):
        '''点击打开更多评论的按钮，基本没问题！'''
        time.sleep(randint(3, 8)/9)
        to_click_ele_xpath = '//*[starts-with(@id, "moreComments")]/div[2]/p'  # /p
        to_click_eles = self.driver.find_elements(By.XPATH, to_click_ele_xpath)  # 先暂时拿掉这个测试一下~
        
        if not click or len(to_click_eles) == 0:
            return None
        for ele in tqdm(to_click_eles, desc='点击more replys'):
            # ActionChains(self.driver).move_to_element(ele).pause(randint(3, 8)/7).click().perform()
            try:
                self.driver.execute_script('arguments[0].click();', ele)
            except Exception as e:
                # print(e)
                pass
            time.sleep(randint(6, 8)/10)
        return self
            
    def click_more_reply_recursively(self):
        time.sleep(randint(3, 8)/5)
        res = self.click_more_reply()
        while res is not None:
            res = self.click_more_reply()
        return self

    def get_comment_low_ele(self):
        comment_container_xpath_lows = ['//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[3]/div[5]/div/div/div',
                                        '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[3]/div[6]/div/div/div',
                                        '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[3]/div[4]/div/div/div']
        for comment_container_xpath_low in comment_container_xpath_lows:
            try:
                WebDriverWait(self.driver, 10, 1).until(
                            EC.presence_of_element_located((By.XPATH, comment_container_xpath_low))
                            )
                res = self.driver.find_element(By.XPATH, comment_container_xpath_low)
                return res
            except Exception:
                # 超时，换令一个就好了，这是因为有广告会这样TT
                pass
            
        
        raise Exception('无法获取comment主界面')

    def click_expand(self):
        comment_container_elements = self.get_comment_low_ele() 
        comment_elements = comment_container_elements.find_elements(By.XPATH, "./*")
        to_click_eles = []  # 这一阶段需要点击的
        for ele in comment_elements:
            com_ele = ele.find_element(By.XPATH, "./div/div/div")
            comment_main_content_eles = com_ele.find_elements(By.XPATH, './div[2]/div[2]/div') 
            if len(comment_main_content_eles) == 1: # 说明是被折叠的评论
                text = comment_main_content_eles[0].text
                # print('text is:', text)
                if 'moderator' not in text and 'deleted' not in text:  # 剔除一些被moderator删除的评论
                    to_click_eles += com_ele.find_elements(By.XPATH, './div[2]/button')
        
        for ele in tqdm(to_click_eles, desc='点击 expand'):
            # ActionChains(self.driver).move_to_element(ele).pause(randint(3, 8)/7).click().perform()
            try:
                ActionChains(self.driver).move_to_element(ele).pause(randint(3, 8)/17).click(ele).perform()
                # self.driver.execute_script('arguments[0].click();', ele)
            except Exception as e:
                # print(e)
                pass
            time.sleep(randint(6, 8)/10)

        return self

    def extract_all_comments(self):
        # comment_container_xpath_high = '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[3]/div[5]'
        comment_container_elements = self.get_comment_low_ele()
        comment_elements = comment_container_elements.find_elements(By.XPATH, "./*")

        #print(len(comment_elements))
        self.comment_data_l = []   # 每次运行一个界面会清零
        for ele in tqdm(comment_elements, desc='抓取评论'):
            comment_data_dict = self.extract_info_of_one_comment_element(ele)
            if comment_data_dict is not None: self.comment_data_l.append(comment_data_dict)
        
        # 接下来就做处理，生成reply comment的信息了

    def parse_data_info_dict_l(self, comment_data_l):
        comment_stack = []  # 评论栈，用来，这个后面再说吧，后面再parse

    def extract_info_of_one_comment_element(self, com_ele):
        '''从一个评论的element内获取信息的函数
            return dict 说明是数据
            return None 说明是非评论的其他div
        '''
        info_dict = dict()
        com_ele = com_ele.find_element(By.XPATH, "./div/div/div")
        info_dict['comment_id'] = com_ele.get_attribute("id")
        if len(info_dict['comment_id']) < 2 or info_dict['comment_id'][:2] != 't1':
            return None
        comment_pre_ele = com_ele.find_element(By.XPATH, "./div[1]")  # 到这里的前一个div，可以用这个div下面的东西来判断是几级评论
        comment_main_content_eles = com_ele.find_elements(By.XPATH, './div[2]/div[2]/div')  # 废弃： './div[2]/div[@class="_3tw__eCCe7j-epNCKGXUKk"]'
        info_dict['comment_depth'] = len(comment_pre_ele.find_elements(By.XPATH, "./*"))
        # print(len(comment_main_content_eles))

        if len(comment_main_content_eles) != 3:
            return None   # 说明是被折叠的评论

        user_info_ele, content_ele, vote_info_ele = comment_main_content_eles
        info_dict['author'] = user_info_ele.find_element(By.XPATH, './span/div').text
        
        # 获取评论时间会变麻烦，需要鼠标悬停
        try:
            time_ele = user_info_ele.find_element(By.XPATH, './span/a')
            #self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover'));", time_ele)  # 鼠标悬停，这个没用
            ActionChains(self.driver).move_to_element(time_ele).pause(randint(3, 8)/7).perform()

            time_info_xpath = '/html/body/div[5]/div'
            WebDriverWait(self.driver, 2).until(
                          EC.presence_of_element_located((By.XPATH, time_info_xpath))
                          )
            comment_time_ele = self.driver.find_element(By.XPATH, time_info_xpath)
            info_dict['comment_time'] = comment_time_ele.text
        except Exception:  #
            info_dict['comment_time'] =  time_ele.text  # 如果没有采集到，就读取当前时间和
        info_dict['data_collect_time'] = int(datetime.today().timestamp())

        # 采集content
        # info_dict['comment_text'] = content_ele.text 
        info_dict['comment_text'] = self.read_comment_text(content_ele)
        #print(info_dict['comment_depth'])
        #coment = self.read_comment_text(content_ele)
        #print(info_dict['comment_text'])

        # 采集vote
        info_dict['score'] = vote_info_ele.find_element(By.XPATH, './div').text
        
        return info_dict

    def read_comment_text(self, content_ele):
        ''' 读取element上面的text
        基础版本的  content_ele.text 不够细决定重新来过~
        返回的是list of string 后期拼起来就可以了
        可能会嵌套，但不重要吧，后面都能处理好的'''
        if content_ele.tag_name == 'div':
            childs = content_ele.find_elements(By.XPATH, './*')
            return [self.read_comment_text(child) for child in childs]
        
        if content_ele.tag_name == 'p':
            if len(content_ele.find_elements(By.XPATH, './/a')) > 0:
                script = """
                    var p = arguments[0];
                    var result = [];
                    for (var i = 0; i < p.childNodes.length; i++) {
                        var node = p.childNodes[i];
                        if (node.nodeType === Node.TEXT_NODE) {
                            // 文本节点
                            result.push(node.nodeValue);
                        } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName === 'A') {
                            // <a>元素节点
                            result.push(node.textContent + ' {(' + node.href + ')}');
                        }
                    }
                    return result.join(' ');
                    """
                return [self.driver.execute_script(script, content_ele) + '\n']
            else:
                return content_ele.text + '\n'

        
        #if content_ele.tag_name == 'a':
        #    return content_ele.text + '{[(' + content_ele.get_attribute("href") + ')]}'
        
        if content_ele.tag_name == 'blockquote':
            childs = content_ele.find_elements(By.XPATH, './*')
            return ['<blockquote_start>\n'] + [self.read_comment_text(child) for child in childs] + ['<blockquote_end>\n']
        




    # ------------------------ 接下来是post部分的提取代码 ------------------------
    def extract_post_data(self):
        '''提取post的详细信息，构成post info dict'''
        self.post_data_json = dict()

        post_content_xpath = '//div[@data-test-id="post-content"]'
        WebDriverWait(self.driver, 8).until(
                          EC.presence_of_element_located((By.XPATH, post_content_xpath))
                          )
        post_content_ele = self.driver.find_element(By.XPATH, post_content_xpath)
        # 这个element下有4个div，分别是upvotes，主要内容，空白地方，和 comments数量

        # 获取vote
        score_ele = post_content_ele.find_element(By.XPATH, './div[1]')
        self.post_data_json['score'] = score_ele.text

        # 获取主要内容
        # 这个下面包含了四个div，分别是 author和time，title，link，tag
        main_content_ele = post_content_ele.find_element(By.XPATH, './div[2]/div[1]')
        author_time_ele = main_content_ele.find_element(By.XPATH, './div[1]')
        try:
            self.post_data_json['author_name'] = author_time_ele.find_element(By.XPATH, './/a').get_attribute("href")
        except Exception:
            self.post_data_json['author_name'] ='[deleted]'  
        # 可能还有authentic相关信息
        try:
            self.post_data_json['authentic'] = author_time_ele.find_element(By.XPATH, './/div[starts-with(@style, "background-color:")]').text
        except Exception:
            pass

        # 鼠标悬停获取时间
        try:
            time_ele = author_time_ele.find_element(By.XPATH, './/span[@data-testid="post_timestamp"]')
            #self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover'));", time_ele)  # 鼠标悬停，这个没用
            ActionChains(self.driver).move_to_element(time_ele).pause(randint(3, 8)/2).perform()

            time_info_xpath = '/html/body/div[5]/div'  #'.//div[@class="subredditvars-r-science"]/div'
            '''WebDriverWait(self.driver, 3).until(
                          EC.presence_of_element_located((By.XPATH, time_info_xpath))
                          )'''
            time_detail_info_ele = self.driver.find_element(By.XPATH, time_info_xpath)
            self.post_data_json['created_time'] = time_detail_info_ele.text
        except Exception:  #
            self.post_data_json['created_time'] =  time_ele.text  # 如果没有采集到，就读取当前时间和

        # 获取title
        title_ele = main_content_ele.find_element(By.XPATH, './div[2]')
        self.post_data_json['title'] = title_ele.find_element(By.XPATH, './/h1').text  # 这个div下的所有title

        # 获取外部链接
        article_origin_link_ele = main_content_ele.find_element(By.XPATH, './div[3]')
        self.article_origin_link = article_origin_link_ele.find_element(By.XPATH, './/a').get_attribute("href")

        # tag
        tag_ele = main_content_ele.find_element(By.XPATH, './div[4]')
        self.post_data_json['tag'] = tag_ele.text # 获取下面的text就好了

        print(self.post_data_json)
        print(self.article_origin_link)
        return self


if __name__ == '__main__':
    spider = CommentSpider()
    spider.log_in()
    curcount = 1
    while True:
        #if check_queue(spider.db, spider.cursor)[0] > 10:
        post_id, created_time, data_collection_time, comment_link = get_task(spider.db, spider.cursor)
        print(f'当前爬取第{curcount}个post：{comment_link}')
        curcount += 1
        spider(comment_link)
    
    
    #spider = CommentSpider()
    #spider.log_in()
    #spider('https://www.reddit.com/r/science/comments/1b6due2/people_who_live_with_social_anxiety_could_be/')
    