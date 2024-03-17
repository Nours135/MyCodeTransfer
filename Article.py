import datetime

import tenacity
from selenium.webdriver.chrome.options import Options
import requests
from lxml import etree
from selenium import webdriver
import time
import re
from selenium.webdriver import Chrome
from utils import get_proxy
from data_connection import store_article, get_article_task, get_db
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    , 'Referer': 'https://www.reddit.com/r/science/'
}


# @tenacity.retry(stop=tenacity.stop.stop_after_attempt(10))
def get_article_page_content(article_origin_link):
    # print(article_origin_link)
    try:
        response = requests.get(article_origin_link, allow_redirects=False, timeout=5, proxies={'https': get_proxy()})
    except:
        print("request请求超时···尝试另一种方式")
        opt = Options()
        # opt.add_argument("--headless")
        opt.add_experimental_option('excludeSwitches', ['enable-automation'])
        opt.add_experimental_option('useAutomationExtension', False)
        #opt.add_argument("--disable-gpu")
        opt.add_argument(f'--proxy-server={get_proxy()}')
        driver = Chrome(options=opt)
        driver.execute_cdp_cmd(   # 似乎也是防止反爬检测的
            'Page.addScriptToEvaluateOnNewDocument',
            {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'}
        )
        driver.get(article_origin_link)
        time.sleep(7)
        html = driver.page_source.encode(encoding='utf-8')
        time.sleep(5)
        driver.close()
        return html

    apparent_encoding = response.apparent_encoding
    status_code = response.status_code
    # print(status_code)

    if status_code == 302:
        return response.headers.get('Location')
    elif status_code == 403 or status_code != 200:
        print("403  or failed ")
        opt = Options()
        # opt.add_argument("--headless")
        opt.add_experimental_option('excludeSwitches', ['enable-automation'])
        opt.add_experimental_option('useAutomationExtension', False)
        #opt.add_argument("--disable-gpu")
        opt.add_argument(f'--proxy-server={get_proxy()}')
        driver = Chrome(options=opt)
        driver.execute_cdp_cmd(   # 似乎也是防止反爬检测的
            'Page.addScriptToEvaluateOnNewDocument',
            {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'}
        )
        driver.get(article_origin_link)
        html = driver.page_source.encode(encoding='utf-8')
        time.sleep(7)
        driver.close()
        return html

    return response.text.encode(apparent_encoding)


def get_titile_content_tables(article_etree):
    title = article_etree.xpath('//title/text()')[0]
    # print(title)

    # title = title[0]

    if len(article_etree.xpath('//main')) == 0:
        res = article_etree.xpath('//h2/text()|//p/strong/text()|//p/text()|//p/a/text()')

    else:
        res = article_etree.xpath(
            '//main//h2/text()|//main//p/strong/text()|//main//p/text()|//main//p/a/text()|//main//strong/text()|//main//b/text()')

    # print(res)
    # res = [re.sub(r'\s{2,}', ' ', re.sub(r'\n', "", r)) for r in res]
    res = [re.sub(r'\s{2,}', ' ', r) for r in res]  # 不替换换行符
    # print(res)
    content = ""
    for r in res:
        content += (r + "\n")
    # print(content)

    tables_list = '没有table'
    tables_etree = article_etree.xpath('//table')
    # print(tables_etree)
    # table
    if len(tables_etree) > 0:
        tables_list = []
        for t in tables_etree:
            one_table = etree.tostring(t)
            tables_list.append(one_table)
            # print(one_table)
        # print(tables_list)
        tables_list = str(tables_list)
    
    imgs_list = '没有img'
    imgs_etree = article_etree.xpath('//img')
    # print(tables_etree)
    # table
    if len(imgs_etree) > 0:
        imgs_list = []
        for t in imgs_etree:
            one_img = etree.tostring(t)
            imgs_list.append(one_img)
            # print(one_table)
        # print(tables_list)
        imgs_list = str(imgs_list)


    return title, str(content), tables_list, imgs_list


def get_one_article(article_origin_link):
    print('article_origin_link: ', article_origin_link)
    data_collection_time = int(datetime.datetime.now().timestamp())
    try:
        article_html = get_article_page_content(article_origin_link)
        article_etree = etree.HTML(article_html)
        title, content, tables, imgs = get_titile_content_tables(article_etree)
    except Exception as e:
        print(e)
        return {'title': "request return nothing !!! please check:  " + article_origin_link, 'content': "null",'tables': "null", 
                'images': imgs,'article_origin_link': article_origin_link, 'data_collection_time': data_collection_time}

    article = {'title': title, 'content': content,'tables': tables, 'images': imgs, 'article_origin_link': article_origin_link,
                'data_collection_time': data_collection_time}
    return article

# ------- 以下内容主要是我加上去的了 ------
def main():
    db = get_db()
    cursor = db.cursor()
    connect_time = datetime.datetime.now().timestamp()
    total_count = 0
    while True:
        if datetime.datetime.now().timestamp() - connect_time > 600:  # 重新连接一下吧
            db = get_db()
            cursor = db.cursor()
            connect_time = datetime.now().timestamp()
        article_origin_link = get_article_task(db, cursor)
        data = get_one_article(article_origin_link)
        status = store_article(article_origin_link, json.dumps(data), db, cursor)
        # 不 sleep 了吧
        if status == 1:
            total_count += 1
            print(f'成功爬取article {total_count} 个。')
        



def test():
    article_origin_link = 'https://news.flinders.edu.au/blog/2023/12/15/why-the-long-face-now-we-know/'
    data = get_one_article(article_origin_link)
    print(data['content'])

    # #     # article_origin_link = 'https://www.psypost.org/2023/12/new-study-links-christian-nationalism-to-increased-prejudice-against-atheists-214829'
    # #     # article_origin_link = 'https://www.eurekalert.org/news-releases/1009788'
   # #     # article_origin_link = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10689938/#d35e555'
    # #     article_origin_link = 'https://www.masseyeandear.org/news/press-releases/2023/11/loss-of-auditory-nerve-fibers-uncovered-in-individuals-with-tinnitus'
    #     article_origin_link = 'https://www.psypost.org/2023/12/playing-a-mobile-game-for-60-minutes-is-enough-to-alter-attentional-network-functions-study-finds-214853'
    #     article_origin_link = ' https://news.flinders.edu.au/blog/2023/12/15/why-the-long-face-now-we-know/'
    #     article_origin_link = 'https://www.yorku.ca/news/2023/12/14/thinking-about-god-inspires-risk-taking-for-believers-york-university-study-finds/'
    article_origin_link = 'https://www.port.ac.uk/news-events-and-blogs/news/facial-symmetry-doesnt-explain-beer-goggles'
    article_origin_link = 'https://psycnet.apa.org/doiLanding?doi=10.1037%2Flhb0000541'
    article_origin_link = 'https://www.usnews.com/news/health-news/articles/2023-12-14/more-research-shows-the-brain-benefits-of-exercise'
     # article_origin_link = 'https://ojs.aaai.org/index.php/AAAI/article/view/26009/25781'
    #data = get_one_article(article_origin_link)
    # print(data)

if __name__ == '__main__':
    main()