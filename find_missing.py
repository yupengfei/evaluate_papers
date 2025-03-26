import json
import os

def find_missing_papers():
    # 读取works_data.json
    with open('works_data.json', 'r', encoding='utf-8') as f:
        works = json.load(f)
    
    # 获取所有works中的ID
    work_ids = set()
    for work in works:
        if 'link' in work:
            # 从链接中提取ID
            work_id = work['link'].split('/')[-1]
            work_ids.add(work_id)
    
    # 获取details目录中已下载的文件ID
    details_dir = 'details'
    downloaded_ids = set()
    for filename in os.listdir(details_dir):
        if filename.endswith('.json'):
            paper_id = filename.replace('work_', '').replace('.json', '')
            downloaded_ids.add(paper_id)
    
    # 找出缺失的ID
    missing_ids = work_ids - downloaded_ids
    
    print(f"总论文数: {len(work_ids)}")
    print(f"已下载数: {len(downloaded_ids)}")
    print(f"缺失数量: {len(missing_ids)}")
    print("\n缺失的论文ID:")
    for missing_id in sorted(missing_ids):
        print(missing_id)
    
    # 返回缺失的ID和对应的链接
    missing_papers = []
    for work in works:
        work_id = work['link'].split('/')[-1]
        if work_id in missing_ids:
            missing_papers.append({
                'id': work_id,
                'link': work['link']
            })
    
    return missing_papers

if __name__ == '__main__':
    missing_papers = find_missing_papers() 