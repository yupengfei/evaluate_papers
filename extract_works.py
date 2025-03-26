from bs4 import BeautifulSoup
import json
import re

def extract_data(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # 找到表格体
    table = soup.find('table', {'id': 'grid-table'})
    rows = table.find('tbody').find_all('tr')
    
    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 12:  # 确保行有足够的列
            continue
            
        # 提取标题和链接
        title_col = cols[2].find('a')
        title = title_col.text if title_col else ''
        link = ''
        if title_col and 'href' in title_col.attrs:
            link = title_col['href'].split('?')[0]
            
        # 提取获奖信息
        award_col = cols[9].find('a')
        award = award_col.text if award_col else ''
        
        record = {
            'number': cols[1].text.strip(),
            'title': title,
            'link': link,
            'user': cols[3].text.strip(),
            'activity': cols[4].text.strip(),
            'type': cols[5].text.strip(),
            'author': cols[6].text.strip(),
            'status': cols[8].text.strip(),
            'award': award,
            'reviewer': cols[10].text.strip(),
            'update_time': cols[11].text.strip()
        }
        data.append(record)
    
    # 保存为JSON文件
    with open('works_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return len(data)

if __name__ == '__main__':
    count = extract_data('Admin _ 作品.html')
    print(f'成功提取 {count} 条记录到 works_data.json') 