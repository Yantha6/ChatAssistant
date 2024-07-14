from herourl import *

def get_hero_story(soup):
    storys_section = soup.find('div', class_='pop-story')
    # print("\r\nstorys_section:")
    # print(storys_section)
    storys = {}
    current_title = '英雄故事'
    storys[current_title] = ""

    if storys_section:
        for element in storys_section.find_all(['p']):
            text = element.get_text(strip=True)
            # 处理标题
            if element.find('font', color="#007ac0"):
                current_title = text
                storys[current_title] = ""
            # 处理内容
            elif current_title:
                storys[current_title] += text + "\n"
    
    return storys



def save_hero_story(hero):
    response = requests.get(hero['url'])
    response.encoding = 'gbk'
    soup = BeautifulSoup(response.text, 'html.parser')

    story = get_hero_story(soup)

    file_path = 'database/herostory/' + f"{hero['name']}_Story_From_Web.txt"
    with open(file_path, 'w', encoding='gbk') as file:
        file.write(f"{hero['name']}的故事\n\n")
        for title, content in story.items():
            file.write(f"{title}\n{content}\n\n")
    print(f"{hero['name']}的故事信息已从网络获取并保存到 {file_path}")
    

def perform_data_crawl():
    hero_urls = get_hero_urls()
    for hero in hero_urls:
        save_hero_story(hero)
    return True

def main():
    hero_urls = get_hero_urls()
    for hero in hero_urls:
        save_hero_story(hero)
    # 测试单个英雄
    # hero_urls = get_hero_urls()
    # print("heros:")
    # print(hero_urls[1],'\n')
    # save_hero_story(hero_urls[1])
    
if __name__ == '__main__':
    main()