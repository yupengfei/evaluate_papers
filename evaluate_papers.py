import os
import json
import csv
import time
from deepseek import DeepSeekClient

def read_paper(file_path):
    """读取JSON文件中的论文内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return {
            'id': data['ID'],
            'title': data['标题'],
            'content': data['内容'],
            'author': data['作者'],
            'unit': data['单位名称']
        }

def save_evaluation(paper_id, evaluation, output_dir='evaluations'):
    """保存单篇论文的评估结果"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filename = os.path.join(output_dir, f'evaluation_{paper_id}.json')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(evaluation, f, ensure_ascii=False, indent=2)

def parse_evaluation(response):
    """解析DeepSeek的响应，提取分数和评语"""
    try:
        # 查找等级（一等奖、二等奖、三等奖、优秀奖、无奖）
        import re
        level_match = re.search(r'等级[:：]\s*(一等奖|二等奖|三等奖|优秀奖|无奖)', response)
        level = level_match.group(1) if level_match else None
        
        # 提取评语（假设评语在"评语："之后）
        comment_match = re.search(r'评语[:：]([\s\S]+?)(?=等级[:：]|$)', response)
        comment = comment_match.group(1).strip() if comment_match else response
        
        return {
            'level': level,
            'comment': comment,
            'full_response': response
        }
    except Exception as e:
        print(f"解析评估结果时出错: {e}")
        return {
            'level': None,
            'comment': response,
            'full_response': response
        }

def append_to_csv(csv_file, row, headers=None):
    """将一行数据追加到CSV文件中"""
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        if not file_exists and headers:
            writer.writerow(headers)
        writer.writerow(row)

def main():
    # 初始化DeepSeek客户端
    API_KEY = ""
    client = DeepSeekClient(API_KEY)
    
    # 准备CSV文件
    csv_file = 'paper_evaluations.csv'
    csv_headers = ['论文ID', '标题', '作者', '单位', '分数', '评语']
    
    # 如果CSV文件不存在，创建它
    if not os.path.exists(csv_file):
        append_to_csv(csv_file, [], csv_headers)
    
    # 读取已经评估过的论文ID
    evaluated_ids = set()
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                evaluated_ids.add(row['论文ID'])
    
    # 遍历details目录下的所有JSON文件
    details_dir = 'details'
    total_files = len([f for f in os.listdir(details_dir) if f.endswith('.json')])
    
    for i, filename in enumerate(os.listdir(details_dir), 1):
        if not filename.endswith('.json'):
            continue
        
        file_path = os.path.join(details_dir, filename)
        print(f"\n处理第 {i}/{total_files} 篇论文: {filename}")
        
        try:
            # 读取论文内容
            paper = read_paper(file_path)
            
            # 如果已经评估过，跳过
            if paper['id'] in evaluated_ids:
                print(f"论文 {paper['id']} 已经评估过，跳过")
                continue
            
            # 构建提示词
            user_prompt = f"""
            标题：{paper['title']}
            
            内容：{paper['content']}
            
            请对这篇论文进行等级评定（一等奖、二等奖、三等奖、优秀奖、无奖）并给出详细评语。应注意 
            1. 如果存在原创性问题或小学化倾向，则直接评0分，并在评语中写明原因。
            2. 字数应该在3000-4000字之间，如果字数少于1000字，则直接评0分，并在评语中写明原因。
            3. 作品非原创、抄袭率高达70%以上，则直接评0分，并在评语中写明原因。
            
            请按以下格式输出：
            评语：（具体评语内容，200字以内）
            等级：（一等奖、二等奖、三等奖、优秀奖、无奖）
            """
            
            # 调用DeepSeek API
            response = client.generate_text(
                system_prompt="""
                你是一位幼儿教育领域的教育专家，当前是2025年3月，你是2025年第十四届幼儿教师优秀论文征集活动的评委。你的评级倾向和标准如下：

 1. 获得不同等级奖项的论文特点
# 一等奖论文：
- **理论深度与实践结合**：论文有明确的理论框架（如陶行知"六大解放"思想、学习故事评价体系），并能将理论深度融入实践案例中。例如，一等奖论文《"六大解放"教育思想赋能户外建构游戏的实践的新路径》详细描述了如何将理论应用于具体游戏场景。
- **创新性**：提出新颖的教学方法或路径，如《绘本为翼：二十四节气文化在幼儿园德育中的生动演绎》中利用绘本将抽象节气文化具象化。
- **实证支持**：有具体的观察记录、案例分析或数据支持（如幼儿行为变化、参与率提升等）。
- **结构严谨**：摘要清晰，关键词准确，正文逻辑严密，参考文献规范且权威。

# 二等奖论文：
- **主题明确但创新性稍弱**：如《基于二十四节气的幼儿园德育课程构建与实施》虽然主题清晰，但理论应用和实践深度略逊于一等奖。
- **实践性强**：注重具体操作策略，但理论支撑相对单薄。例如，《随儿童视角——中班幼儿自由角色区路径探究》详细描述了材料投放和主题选择，但缺乏理论升华。
- **数据或案例较少**：虽有实践描述，但量化数据或长期效果分析不足。

# 三等奖论文：
- **常规主题**：如《"自主游戏"情境下师幼互动策略的有效性研究》探讨常见问题，但缺乏新颖视角。
- **泛泛而谈**：策略描述较多，但具体案例或数据支持不足。例如，《幼儿园游戏化教学实践研究》提出"游戏化教学"但未深入分析其独特效果。
- **结构完整但深度不足**：参考文献较少或不够权威。

# 优秀奖论文：
- **内容空洞或偏离主题**：如《幼儿游戏创造性学习与发展的核心动力》泛谈游戏价值，缺乏具体实践或理论支撑。
- **缺乏实证**：多为描述性内容，如《自主游戏——使每一名幼儿闪闪发光》虽有案例，但分析浅显。
- **格式问题**：参考文献不规范或缺失。

# 无奖论文：
- **严重偏离主题**：如《以"数"为媒，碰撞精彩》讨论数字技术，与幼儿教育关联薄弱。
- **学术性差**：如《小学语文阅读教学中核心素养培养的策略研究》完全脱离幼儿教育领域。
- **无实践支撑**：纯理论堆砌或空泛建议。

---

 2. 评委最看重的因素
# 核心因素：
- **理论与实践的融合**：评委明显偏好能将经典理论（如陶行知思想、多元智能理论）与具体教学场景结合的论文。例如，一等奖论文均引用权威理论并展示落地效果。        
- **创新性和独特性**：新颖的主题或方法（如"学习故事""沉浸式节气教育"）更易获高分。
- **实证支持**：案例、数据、长期观察记录（如幼儿行为变化、参与率提升）是重要加分项。

# 次要因素：
- **结构规范性**：摘要、关键词、正文、参考文献的完整性和学术规范。
- **语言表达**：逻辑清晰，专业术语使用准确，文风严谨。

---

 3. 评委特别喜欢的论文类型
- **文化传承与创新**：如将二十四节气、传统手工艺等融入幼儿教育的论文（一等奖《绘本为翼》）。
- **儿童主体性**：强调幼儿自主性、教师角色转变的研究（一等奖《学习故事在角色游戏中的有效运用》）。
- **跨领域整合**：结合心理学、教育学等多学科视角（如引用皮亚杰、维果茨基理论）。

---

 4. 评委特别不喜欢的论文类型
- **脱离幼儿教育实际**：如无奖论文讨论小学语文或数字技术，与幼儿教育无关。
- **泛泛而谈**：仅描述游戏重要性而无具体策略或案例（优秀奖《幼儿游戏创造性学习与发展的核心动力》）。
- **缺乏理论支撑**：仅罗列实践操作，未引用任何权威理论或文献。

---

 5. 清晰的评分标准总结
| **评分维度**       | **高分要求（一等奖）**                          | **低分表现（无奖/优秀奖）**              |
|--------------------|-----------------------------------------------|----------------------------------------|
| **理论深度**       | 引用经典理论并创造性应用（如陶行知、多元智能） | 无理论或理论生搬硬套                   |
| **实践创新**       | 提出新方法、路径，且有实证案例支持             | 常规策略或空洞描述                     |
| **实证支持**       | 详细数据、长期观察记录、幼儿行为分析           | 无数据或仅泛泛而谈                     |
| **结构规范性**     | 摘要清晰、参考文献权威、逻辑严密               | 格式混乱、参考文献缺失                 |
| **语言表达**       | 专业术语准确，文风严谨                         | 口语化或逻辑不清                       |
| **主题相关性**     | 紧扣幼儿教育核心问题（游戏、德育、文化传承）   | 偏离主题（如讨论小学语文、数字技术）   |

---

 6. 其他
- **评委偏好行动研究**：一等奖论文多采用"问题-策略-效果"的行动研究框架（如《学习故事》论文中的"注意-识别-回应"三步法）。
- **反对形式化**：单纯堆砌理论或罗列活动流程的论文（如优秀奖《新时代背景下幼儿教育的创新与实践》）难以获奖。
- **注重细节**：即使是小班幼儿的个案观察（如二等奖《小班幼儿阅读区活动的现状及指导策略》）也能获奖，但需分析深入。

综上，评委的评级标准高度强调**理论指导下的实践创新**，尤其看重论文对幼儿教育实际问题的解决能力和文化传承价值。
                
                """,
                user_prompt=user_prompt,
                temperature=1.0,
                max_tokens=1000,
                top_p=0.7
            )
            print(response)
            
            if response:
                # 解析评估结果
                evaluation = parse_evaluation(response)
                
                # 保存单独的评估文件
                save_evaluation(paper['id'], evaluation)
                
                # 写入CSV
                row = [
                    paper['id'],
                    paper['title'],
                    paper['author'],
                    paper['unit'],
                    evaluation['level'],
                    evaluation['comment']
                ]
                append_to_csv(csv_file, row)
                
                print(f"完成论文评估 - ID: {paper['id']}, 等级: {evaluation['level']}")
            
            # 等待1秒避免API限制
            time.sleep(1)
            
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")
            continue

if __name__ == '__main__':
    main() 