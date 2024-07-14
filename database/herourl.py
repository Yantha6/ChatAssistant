import requests
from bs4 import BeautifulSoup

# 获取所有英雄URL的函数
def get_hero_urls():
    hero_urls = []
    base_url = 'https://pvp.qq.com/web201605/'
    hero_list_url = 'herolist.shtml'
    response = requests.get(base_url + hero_list_url)
    response.encoding = 'gbk'
    #response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找包含所有英雄URL的元素
    hero_list = soup.find('ul', class_='herolist clearfix')
    for li in hero_list.find_all('li'):
        a_tag = li.find('a')
        if a_tag:
            hero_name = a_tag.get_text()  # 获取<a>标签的文本内容
            hero_url = a_tag['href']
            hero_urls.append({'name': hero_name, 'url': base_url+hero_url})
    
    # 打印所有英雄的URL
    
    #print("hero_urls:\n",hero_urls)
    return hero_urls