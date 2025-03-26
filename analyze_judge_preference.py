import os
import json
from deepseek import DeepSeekClient
import time

def read_awarded_papers(details_dir):
    """读取所有有获奖等级的论文"""
    papers = []
    for filename in os.listdir(details_dir):
        if not filename.endswith('.json'):
            continue
            
        file_path = os.path.join(details_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data['获奖等级']:  # 只收集有获奖等级的论文
                papers.append({
                    'title': data['标题'],
                    'content': data['内容'],
                    'award': data['获奖等级']
                })
    
    # 按奖项排序
    award_order = {'一等奖': 1, '二等奖': 2, '三等奖': 3, '优秀奖': 4, '无奖': 5}
    papers.sort(key=lambda x: award_order.get(x['award'], 999))
    return papers

def analyze_judge_preference(client, papers):
    """让DeepSeek分析评委的评级倾向"""
    # 构建示例数据
    examples = []
    for paper in papers:
        # 为每个奖项选择前3篇论文作为示例
        award_count = sum(1 for p in examples if p['award'] == paper['award'])
        if award_count < 3:
            examples.append(paper)
    
    # 构建提示词
    prompt = """我给你一些已经评级的论文样本，请分析这位评委的评级倾向和标准。
    这些论文都来自"第十四届幼儿教师优秀论文征集活动"，奖项从高到低分别是：一等奖、二等奖、三等奖、优秀奖、无奖。

    请分析以下几个方面：
    1. 获得不同等级奖项的论文有什么特点？
    2. 评委在评判时最看重哪些因素？
    3. 评委特别喜欢什么样的论文？
    4. 评委特别不喜欢什么样的论文？
    5. 能否总结出一个清晰的评分标准？

    以下是部分获奖论文示例：

    """
    
    # 添加示例论文
    for paper in examples:
        prompt += f"\n=== {paper['award']} 论文示例 ===\n"
        prompt += f"标题：{paper['title']}\n"
        prompt += f"内容：{paper['content']}\n"
    
    prompt += "\n请基于以上论文样本，详细分析评委的评级倾向和标准。分析要具体且有理有据。"
    
    # 调用DeepSeek API
    response = client.generate_text(
        system_prompt="你是一位资深的教育领域论文评审专家，擅长分析评审标准和倾向。",
        user_prompt=prompt,
        temperature=0.7,
        max_tokens=2000,
        top_p=0.9
    )
    
    return response

def main():
    # 初始化DeepSeek客户端
    API_KEY = ""
    client = DeepSeekClient(API_KEY)
    
    # 读取获奖论文
    print("正在读取获奖论文...")
    papers = read_awarded_papers('details')
    print(f"找到 {len(papers)} 篇获奖论文")
    
    # 分析评委倾向
    print("\n开始分析评委的评级倾向...")
    analysis = analyze_judge_preference(client, papers)
    
    # 保存分析结果
    results = {
        'total_papers': len(papers),
        'award_distribution': {award: len([p for p in papers if p['award'] == award]) 
                             for award in ['一等奖', '二等奖', '三等奖', '优秀奖', '无奖']},
        'analysis': analysis
    }
    
    with open('judge_preference_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n分析结果：")
    print(analysis)
    print("\n详细结果已保存到 judge_preference_analysis.json")

if __name__ == '__main__':
    main() 