##################################################
## Project: PTT Goods Trace
## Author: {Chun}
## Version: {190827}
## Status:
##################################################

# PTT Crawl and Parse Requirements
import requests
from bs4 import BeautifulSoup
import ast

# Gmail API Requirements
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes, os

# Google API Credentials Requirements
import httplib2
from apiclient import discovery
from oauth2client.file import Storage
from oauth2client import file, client, tools
import gmail

# Multipleprocessing
from multiprocessing import Pool
import queue
import time
import threading


def get_lastPage(url):
    """ Get the url of next page
    
    Parameters
    ----------
    url : str
        the url of current page

    """

    # url = 'https://www.ptt.cc//bbs/MacShop/index15527.html'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    result = soup.select('.btn-group.btn-group-paging a')

    last_page = [a for a in result if a.text == '‹ 上頁'][0].get('href')
    return last_page


def crawl_list(page):
    """ Get the list of urls of current page
    
    Parameters
    ----------
    page : str
        the url of current page

    """

    html = requests.get(page).text
    soup = BeautifulSoup(html, 'html.parser')

    domain_prefix = 'https://www.ptt.cc'
    # skip = []
    result = soup.select('.title a')

    url_list = []
    for i in result:
        if i.text.split(' ')[0] == '[販售]' :
            url_list.append(
                {'url':domain_prefix + i['href'], 
                'title': i.text
                }
            )
    return url_list


def parse_content(article):
    """ Parse the contets of a article.
    
    Parameters
    ----------
    article : str
        the url of article

    """

    def parse_meta(soup):
        metaline = soup.select('.article-metaline')
        # print(metaline)

        def parse_title(metaline):
            try:
                title = metaline[1].text
                return title.split('標題')[1].strip()
            except:
                return ''

        def parse_author(metaline):
            try:
                author = metaline[0].text
                return author.split('作者')[1].strip()
            except:
                return ''

        def parse_datetime(metaline):
            try:
                datetime = metaline[2].text
                return datetime.split('時間')[1].strip()
            except:
                return ''

        meta = {'title': parse_title(metaline),
                'author': parse_author(metaline),
                'datetime': parse_datetime(metaline)
                }
        return meta

    def parse_goodInfo(soup):
        field = ['[物品型號]', '[物品規格]', '[保固日期]', '[原始發票]', '[隨機配件]',
                '[照片連結]', '[拍賣連結]', '[連絡方式]', '[交易地點]', '[交易方式]',
                '[交易價格]', '[其他備註]']
        good_info = {}
        for k in field:
            good_info[k] = ''

        content = soup.select('#main-content')[0].text.split('--')[0]
        l = [content.find(i) for i in field]
        l.append(len(content))

        for i in range(len(l)):
            if(l[i] < 0):
                good_info[field[i]] = ''
            else:
                try:
                    h = t + 8
                    t = l[i] - 1
                    good_info[field[i-1]] = content[h:t].strip()
                except:
                    t = l[i] - 1
        
        return good_info

    html = requests.get(article).text
    soup = BeautifulSoup(html, 'html.parser')
    return {'meta': parse_meta(soup),
            'good_info': parse_goodInfo(soup)}


def goodTrace(target, articles):
    """ Check if article contains the goods we are tracing.
    
    Parameters
    ----------
    target : str
        the name of tracing goods.
    articles: list
        the list of urls of articles

    """
    target_list = []
    f = open('product_dic')
    proDic = ast.literal_eval(f.read())

    for a in articles:
        # print(i['content']['good_info']['[物品型號]'])
        if sum([k in a['title'] for k in proDic.get(target)]):
            target_list.append(a)

    return target_list


def main(u):
    # crawl list
    articles = goodTrace(target_good, crawl_list(u))

    # parse content
    for a in articles:
        data.append({'url': a['url'],
                    'content': p.apply_async(parse_content, args=(a['url'],)).get()})
        # html = requests.get(a['url']).text
        # content = parse_content(a['url'])


if __name__ == '__main__':
    start_time = time.time()
    site = 'https://www.ptt.cc'
    board = 'bbs/MacShop'
    page = 'index.html'
    url = ('/').join([site, board, page])
    target_good = 'MacBook'
    p = Pool(4)

    data = []
    threads=[]

    for i in range(10):
        print(url)    
        threads.append(threading.Thread(target=main, args=(url,)))
        threads[i].start()

        # get last page
        last_page = get_lastPage(url)
        url = ('/').join([site, last_page])
        # print(url)
    
    for t in threads:
        t.join()
    end_time = time.time()
    print('程序時間共{}秒'.format(end_time - start_time))
    print(data) 

    # # Send Gmail
    # credentials = gmail.get_credentials()
    # http = credentials.authorize(httplib2.Http())
    # service = discovery.build('gmail', 'v1', http=http)
    
    # user_profile = service.users().getProfile(userId='me').execute()
    # sender_email = user_profile['emailAddress']
    # print(sender_email)

    # content = ''
    # for item in data:
    #     meta = item['content']['meta']
    #     good_info = item['content']['good_info']

    #     content += ('\n').join([meta['title'], '[物品規格]: '+good_info['[物品規格]'], '[交易地點]: '+good_info['[交易地點]'], '[交易方式]: '+good_info['[交易方式]'], '[交易價格]; '+good_info['[交易價格]'], item['url']])
    #     content +='\n\n'
    #     content += '------------------------------------------------------------\n'
    #     content +='\n\n'

    # # print(content)
    # title = ('').join(['您追蹤的', target_good, '有', str(len(data)), '則新貼文！'])
    
    # mes = gmail.CreateMessage(sender_email, sender_email, data, target_good)
    # if mes:
    #     gmail.SendMessage(service, sender_email, mes)
    
