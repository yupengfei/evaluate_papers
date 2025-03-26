import json
import requests
from bs4 import BeautifulSoup
import time
import os

def read_cookie_file(cookie_file):
    with open(cookie_file, 'r', encoding='utf-8') as f:
        return f.read().strip()

def extract_text_from_field(container, label):
    field = container.find('span', string=label)
    if field:
        box = field.find_parent('div', class_='form-group').find('div', class_='box-body')
        if box:
            return box.get_text(strip=True)
    return ''

def download_and_parse_detail(url, cookies):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Cookie': cookies
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        form_container = soup.find('div', class_='form-horizontal')
        
        if not form_container:
            print(f"无法在页面中找到内容: {url}")
            return None
            
        # 提取所有需要的字段
        data = {
            'ID': extract_text_from_field(form_container, 'ID'),
            '用户': extract_text_from_field(form_container, '用户'),
            '活动': extract_text_from_field(form_container, '活动'),
            '类型名称': extract_text_from_field(form_container, '类型名称'),
            '标题': extract_text_from_field(form_container, '标题'),
            '作者': extract_text_from_field(form_container, '作者'),
            '单位名称': extract_text_from_field(form_container, '单位名称'),
            '省市': extract_text_from_field(form_container, '省市'),
            '内容': extract_text_from_field(form_container, '内容'),
            '链接名称': extract_text_from_field(form_container, '链接名称'),
            '链接说明': extract_text_from_field(form_container, '链接说明'),
            '链接': extract_text_from_field(form_container, '链接'),
            '获奖等级': extract_text_from_field(form_container, '获奖等级'),
            '获奖评语': extract_text_from_field(form_container, '获奖评语'),
            '创建时间': extract_text_from_field(form_container, '创建时间'),
            '更新时间': extract_text_from_field(form_container, '更新时间')
        }
        
        return data
        
    except Exception as e:
        print(f"下载或解析页面时出错 {url}: {str(e)}")
        return None

def main():
    # 创建保存详情的目录
    if not os.path.exists('details'):
        os.makedirs('details')
    
    # 读取cookie
    cookies = read_cookie_file('cookie')
    
    # 读取works_data.json
    with open('works_data.json', 'r', encoding='utf-8') as f:
        works = json.load(f)
    
    total = len(works)
    for i, work in enumerate(works, 1):
        url = work['link']
        if not url:
            print(f"跳过记录 {i}/{total}: 无效链接")
            continue
            
        print(f"正在处理 {i}/{total}: {url}")
        
        # 下载和解析详情
        detail_data = download_and_parse_detail(url, cookies)
        
        if detail_data:
            # 保存为单独的JSON文件
            filename = f"details/work_{detail_data['ID']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(detail_data, f, ensure_ascii=False, indent=2)
            print(f"已保存: {filename}")
        
        # 等待1秒
        time.sleep(1)

if __name__ == '__main__':
    main() 