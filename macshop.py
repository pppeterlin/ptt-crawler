import requests
from bs4 import BeautifulSoup

def last_page(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    result = soup.select('.btn-group.btn-group-paging a')

    last_page = [a for a in result if a.text == '‹ 上頁'][0].get('href')
    return last_page


def crawl_list(page):
    html = requests.get(page).text
    soup = BeautifulSoup(html, 'html.parser')

    domain_prefix = 'https://www.ptt.cc'
    skip = []
    result = soup.select('.title a')

    url_list = []
    for i in result:
        if i.text.split(' ')[0] == '[販售]' :
            url_list.append(domain_prefix + i['href'])
    return url_list


def parse_content(article):

    def parse_meta(soup):
        metaline = soup.select('.article-metaline')

        def parse_title(metaline):
            title = metaline[1].text
            return title.split('標題')[1].strip()

        def parse_author(metaline):
            author = metaline[0].text
            return author.split('作者')[1].strip()

        def parse_datetime(metaline):
            datetime = metaline[2].text
            return datetime.split('時間')[1].strip()

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
            good_info[k] = None

        content = soup.select('#main-content')[0]
        for i in range(len(field)):
            try:
                info = content.text.split(field[i])[1].split(field[i+1])[0].split('：')[1]
                good_info[field[i]] = info.strip()
            except:
                good_info[field[i]] = None

        return good_info

    html = requests.get(article).text
    soup = BeautifulSoup(html, 'html.parser')
    return {'meta': parse_meta(soup),
            'good_info': parse_goodInfo(soup)}

if __name__ == '__main__':
    site = 'https://www.ptt.cc'
    board = 'bbs/MacShop'
    page = 'index.html'
    url = ('/').join([site, board, page])

    data = []
    for i in range(1):
        articles = crawl_list(url)
        for a in articles:
            # html = requests.get(a).text
            content = parse_content(a)
            data.append({'url': a, 'content': content})

        last_page = last_page(url)
        url = last_page

    print(data)
