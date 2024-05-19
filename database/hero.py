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
    
    return hero_urls

def get_skills_info(soup):
    skills_section = soup.find('div', class_='skill-show')
    skills = {}
    if skills_section:
        for skill in skills_section.find_all('div', class_='show-list'):
            skill_name = skill.find('b').get_text()
            #如果skill_name为空，跳过
            if not skill_name:
                continue
            skill_name_element = skill.find('p', class_='skill-name')
            if skill_name_element:
                cool_down = skill_name_element.find('span', string=lambda x: '冷却值' in x).get_text().replace('冷却值：', '')
                cost = skill_name_element.find('span', string=lambda x: '消耗' in x).get_text().replace('消耗：', '')
            skill_description = skill.find('p', class_='skill-desc').get_text()
            skills[skill_name] = {
                'description': skill_description.strip(),
                'cool_down': cool_down,
                'cost': cost
            }
    return skills

def get_skills_advice(soup):
    skill_advice_section = soup.find('div', class_='sugg-info2 info')
    skills_advice = {}
    # print("\r\nskill_advice_section:")
    # print(skill_advice_section)
    if skill_advice_section:
        sugg_names = skill_advice_section.find_all('p', class_='sugg-name')
        skills_advice['main_skill'] = sugg_names[0].find('span').get_text()
        skills_advice['sub_skill'] = sugg_names[1].find('span').get_text()
        skills_advice['summoner_skill'] = skill_advice_section.find('p', class_='sugg-name sugg-name3').find('span').get_text()
    return skills_advice

def get_mingwen_info(soup):
    mingwen_section = soup.find('div', class_='sugg rs fl')
    mingwens = []
    # print("\r\nmingwen_section:")
    # print(mingwen_section)
    if mingwen_section:
        mingwen_list = mingwen_section.find('ul', class_='sugg-u1')
        for mingwen in mingwen_list.find_all('li'):
            mingwen_name = mingwen.find('em').get_text()
            mingwen_description = mingwen.find_all('p')
            mingwen_desc = ' '.join(p.get_text() for p in mingwen_description)
            mingwens.append({
                'name': mingwen_name,
                'description': mingwen_desc.strip()
            })
        mingwen_advice = mingwen_section.find('p', class_='sugg-tips').get_text()
    return mingwens, mingwen_advice


def get_equip_info(soup):
    equip_section = soup.find('div', class_='equip-bd')
    equip_info = []
    equip_advice_list = []
    if equip_section:
        equip_infos = equip_section.find_all('div', class_='equip-info l')
        for equip_info_div in equip_infos:
            equip_list = equip_info_div.find('ul', class_='equip-list')
            equip_list_info = []
            for equip in equip_list.find_all('li'):
                equip_name = equip.find('p').get_text()
                item_detail = equip.find('div', class_='itemFromTop')
                if item_detail:
                    name_elem = item_detail.find('h4', id='Jname')
                    price_elem = item_detail.find('p', id='Jprice')
                    total_price_elem = item_detail.find('p', id='Jtprice')
                    desc_elem = item_detail.find('div', class_='item-desc')
                    
                    if name_elem and price_elem and total_price_elem and desc_elem:
                        equip_info.append({
                            'name': name_elem.get_text(),
                            'price': price_elem.get_text().replace('售价：', ''),
                            'total_price': total_price_elem.get_text().replace('总价：', ''),
                            'description': desc_elem.get_text(separator=' ').strip()
                        })
                else:
                    equip_info.append({'name': equip_name})
            equip_advice = equip_info_div.find('p', class_='equip-tips').get_text()
            equip_advice_list.append(equip_advice)
    return equip_info, equip_advice_list

def get_hero_relation(soup):
    hero_relation_section = soup.find('div', class_='hero-info-box')
    hero_relation_info = {}
    # print("\r\nhero_relation_section:")
    # print(hero_relation_section)
    if hero_relation_section:
        hero_relations = hero_relation_section.find_all('div', class_='hero-info l info')
        for hero_relation in hero_relations:
            hero_relation_name = hero_relation.find('div', class_='hero-f1 fl').get_text().strip()
            hero_relation_info_text = hero_relation.find('div', class_='hero-list-desc').find_all('p')
            full_text = ' '.join(p.get_text().strip() for p in hero_relation_info_text)
            hero_relation_info[hero_relation_name] = full_text
    return hero_relation_info


def save_hero_info(hero):
    response = requests.get(hero['url'])
    response.encoding = 'gbk'
    soup = BeautifulSoup(response.text, 'html.parser')

    response_withex = response.text.replace('<!--', '').replace('-->', '')
    soup_withex = BeautifulSoup(response_withex, 'html.parser')

    skills = get_skills_info(soup)
    skills_advice = get_skills_advice(soup)
    mingwens, mingwen_advice = get_mingwen_info(soup_withex)
    equip_info, equip_advice = get_equip_info(soup_withex)
    hero_relation = get_hero_relation(soup_withex)
    
    file_path = 'database/heroinfo/' + f"{hero['name']}_Info_From_Web.txt"
    with open(file_path, 'w', encoding='gbk') as file:
        file.write(f"{hero['name']}的信息\n\n")
        skill_labels = ["被动", "技能1", "技能2", "技能3"]

        file.write("技能信息:\n")
        for index, (skill_name, skill_info) in enumerate(skills.items()):
            label = skill_labels[index] if index < len(skill_labels) else f"技能{index}"
            file.write(f"{label} - {skill_name}:\n")
            file.write(f"描述: {skill_info['description']}\n")
            file.write(f"冷却值: {skill_info['cool_down']}\n")
            file.write(f"消耗: {skill_info['cost']}\n\n")
        file.write("技能加点建议:\n")
        file.write(f"主生: {skills_advice['main_skill']}\n")
        file.write(f"副生: {skills_advice['sub_skill']}\n")
        file.write(f"召唤师技能: {skills_advice['summoner_skill']}\n\n")

        file.write("铭文信息:\n")
        for mingwen in mingwens:
            # file.write(f"\n{mingwen['name']}:")
            file.write(f"{mingwen['description']}\n")
        file.write("铭文建议:\n")
        file.write(f"{mingwen_advice}\n")

        file.write("\n出装:\n")
        for index, item in enumerate(equip_info, 1):
            file.write(f"装备{index}: {item['name']}")
            if 'price' in item:
                file.write(f"售价: {item['price']} ")
            if 'total_price' in item:
                file.write(f"总价: {item['total_price']} ")
            if 'description' in item:
                file.write(f"描述: {item['description']} ")
            file.write("\n")
        file.write("\n装备推荐:\n")
        for advice in equip_advice:
            file.write(f"{advice}\n")
            
        file.write("\n英雄关系:\n")
        for relation_type, relation_text in hero_relation.items():
            file.write(f"{relation_type}:\n")
            file.write(f"{relation_text}\n")
    print(f"{hero['name']}的信息已从网络获取并保存到 {file_path}")

def perform_data_crawl():
    hero_urls = get_hero_urls()
    for hero in hero_urls:
        save_hero_info(hero)
    return True

# def main():
#     hero_urls = get_hero_urls()
#     for hero in hero_urls:
#         save_hero_info(hero)
#     # 测试单个英雄
#     # hero_urls = get_hero_urls()
#     # print(hero_urls[1])
#     # save_hero_info(hero_urls[1])
# if __name__ == '__main__':
#     main()