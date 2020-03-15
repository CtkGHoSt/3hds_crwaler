
import requests
import json
import datetime
import sys

import telebot

from bs4 import BeautifulSoup

CHANNEL_ID = sys.argv[1]
TG_CHAT_ID = sys.argv[2]
TG_BOT = sys.argv[3]

def format_date(date):
    if date.find('上') != -1 :
        post_time = datetime.datetime.strptime(date, '%Y年%m月%d日 上午%H:%M')
    elif date[date.find('午')+1:date.find(':')] != '12':
        post_time = datetime.datetime.strptime(date, '%Y年%m月%d日 下午%H:%M')
        post_time = post_time + datetime.timedelta(hours=12)
    else:
        post_time = datetime.datetime.strptime(date, '%Y年%m月%d日 下午%H:%M')
    return post_time
    

def get_3hds_post(url):
    
    res = requests.get(url)
    if res.status_code != 200:
        return {'status':False, 'msg':'status code:' + str(res.status_code)}
    html = res.text
    soup = BeautifulSoup(html, 'html5lib')
    comment_list = soup.find('ol', class_='comment-list')
    all_post = list()
    if comment_list is None:
        return {'status':False, 'msg':'comment_list is None'}
    for comment in comment_list:
        try:
            name = comment.article.footer.find('b')
            name = name.string.strip()
            if name == '方言':
                all_post.append(comment)
        except:
            pass
    result = list()
    for comment in all_post:
        post_contents = comment.find('div', class_='comment-content')
        
        post_time = comment.find('time').string.strip()
        post_string = ' '.join(map(lambda x:str(x).strip() if str(x)!='<br/>' else '', list(post_contents.find('p').contents)))
        post_link = ''
        
        try:
            post_link = post_contents.find('img')['src']
        except:
            post_link = post_contents.find('a')['href']
        
        result.append({
            'index':all_post.index(comment),
            'time':format_date(post_time), 
            'link':post_link,
            'string':post_string
        })
    return {'status':True, 'result':result}


def new_post_link():
    base_url = 'http://2019.3hedashen.me/'
    res = requests.get(base_url)
    if res.status_code != 200:
        return False
    html = res.text
    soup = BeautifulSoup(html, 'html5lib')
    tie = soup.find_all('div', class_='blog-feed-contant')
    tie_link = tie[1].find('a')['href']
    return tie_link

def main():
    gslj_bot = telebot.TeleBot(TG_BOT)
    
    link = new_post_link()
    get_post_res = get_3hds_post(link)
    for item in get_post_res['result']:
        # print(item['time'], item['time'] + datetime.timedelta(hours=10))
        if item['time'] + datetime.timedelta(hours=1) > datetime.datetime.now():
            print(item)
            gslj_bot.send_message(CHANNEL_ID, 
                '发表于：{}\n\n{}\n\n{}'.format(
                    '`{}`'.format(str(item['time'])),
                    '**{}**'.format(item['string']),
                    '[链接]({})'.format(item['link']),
                    '__本频道内容均来自于 3hedashen.me__'
                ), 
                parse_mode='markdown'
            )
    
if __name__ == '__main__':
    gslj_bot = telebot.TeleBot(TG_BOT)
    gslj_bot.send_message(TG_CHAT_ID, '3hedashen crawler begin')
    print(datetime)
    # main()







