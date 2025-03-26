from find_missing import find_missing_papers
from download_details import download_and_parse_detail, read_cookie_file
import json
import time

def download_missing_papers():
    # 获取缺失的论文
    missing_papers = find_missing_papers()
    
    if not missing_papers:
        print("没有发现缺失的论文！")
        return
        
    # 读取cookie
    cookies = read_cookie_file('cookie')
    
    # 下载缺失的论文
    print(f"\n开始下载 {len(missing_papers)} 篇缺失的论文...")
    
    for i, paper in enumerate(missing_papers, 1):
        print(f"\n正在下载第 {i}/{len(missing_papers)} 篇: ID={paper['id']}")
        
        # 下载和解析详情
        detail_data = download_and_parse_detail(paper['link'], cookies)
        
        if detail_data:
            # 保存为JSON文件
            filename = f"details/work_{detail_data['ID']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(detail_data, f, ensure_ascii=False, indent=2)
            print(f"已保存: {filename}")
        
        # 等待1秒
        time.sleep(1)
    
    print("\n下载完成！")

if __name__ == '__main__':
    download_missing_papers() 