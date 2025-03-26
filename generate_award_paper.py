import json
from deepseek import DeepSeekClient
import time
import re

def save_as_markdown(paper_data, output_file='generated_paper.md'):
    """将论文保存为Markdown格式"""
    content = paper_data['内容']
    
    # 提取论文各个部分
    title = paper_data['标题']
    abstract_match = re.search(r'摘要[：:]\s*([\s\S]+?)(?=关键词[：:]|$)', content)
    abstract = abstract_match.group(1).strip() if abstract_match else ""
    
    keywords_match = re.search(r'关键词[：:]\s*([\s\S]+?)(?=正文|$)', content)
    keywords = keywords_match.group(1).strip() if keywords_match else ""
    
    # 构建Markdown内容
    markdown_content = f"""# {title}

## 摘要
{abstract}

## 关键词
{keywords}

## 正文
{content}

---
作者：{paper_data['作者']}
单位：{paper_data['单位名称']}
"""
    
    # 保存为Markdown文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return output_file

def generate_paper():
    # 初始化DeepSeek客户端
    API_KEY = ""
    client = DeepSeekClient(API_KEY)
    
    # 构建system prompt，基于评审专家的偏好
    system_prompt = """
    你是一位专业的学前教育研究专家，擅长撰写高质量的学术论文。你需要创作一篇能够获得一等奖的学前教育论文。
    
    一等奖论文的核心要求：
    1. 理论深度与实践结合：
       - 必须引用经典理论
       - 理论要与实践案例紧密结合
       - 展示理论在具体教学场景中的应用
    
    2. 创新性：
       - 提出新颖的教学方法或路径
       - 结合传统文化元素
       - 注重幼儿主体性
    
    3. 实证支持：
       - 包含具体的观察记录
       - 提供案例分析
       - 有数据支持
    
    4. 结构规范：
       - 摘要清晰
       - 关键词准确
       - 正文逻辑严密
       - 参考文献规范且权威
    
    论文结构要求：
    1. 标题：新颖且体现研究重点
    2. 摘要：300字左右，包含研究目的、方法、结果和结论
    3. 关键词：3-5个
    4. 正文：3000-4000字
    5. 参考文献：至少8篇，包含核心期刊文献
    
    请按照以上要求创作一篇完整的论文。
    """
    
    # 构建user prompt，让AI选择主题
    user_prompt = """
    请从以下学前教育研究领域中选择一个主题，创作一篇能够获得一等奖的论文：

    1. 学前教育方针政策的理论研究和实践
    2. 幼儿园教育教学方法的实践与研究
    3. 幼儿园环境建设的研究与成果
    4. 幼儿园教育评价的策略与实施
    5. 幼儿园管理的创新与实践
    6. 教师专业成长与职业发展
    7. 幼儿园与小学的科学衔接
    8. 幼儿园数字化建设的应用
    9. 幼儿园师德建设工作的实践
    10. 幼儿园游戏活动的探究
    11. 幼儿园家园共育工作
    12. 幼儿园安全保障工作
    13. 幼儿园教研工作

    要求：
    1. 选择一个你认为最有创新性和实践价值的主题
    2. 将主题与经典教育理论紧密结合
    3. 提供具体的实践案例和观察记录
    4. 包含数据分析和效果评估
    5. 展示创新性的解决方案
    6. 字数控制在4000字左右
    
    请先告诉我你选择的主题，然后开始创作论文。
    """
    
    # 调用API生成论文
    response = client.generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7,
        max_tokens=8000,
        top_p=0.9
    )
    
    # 保存生成的论文
    if response:
        # 从响应中提取主题
        title_match = re.search(r'标题[：:]\s*([^\n]+)', response)
        title = title_match.group(1) if title_match else "AI生成的学前教育论文"
        
        paper_data = {
            "ID": "generated_001",
            "标题": title,
            "内容": response,
            "作者": "AI生成",
            "单位名称": "示例幼儿园"
        }
        
        # 保存为JSON文件
        # with open('generated_paper.json', 'w', encoding='utf-8') as f:
        #     json.dump(paper_data, f, ensure_ascii=False, indent=2)
        
        # 保存为Markdown文件
        markdown_file = save_as_markdown(paper_data)
        
        print(f"论文生成完成，主题：{title}")
        print(f"已保存到 {markdown_file}")
        return paper_data
    else:
        print("论文生成失败")
        return None

if __name__ == '__main__':
    generate_paper() 