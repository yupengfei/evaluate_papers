import requests
import json


class DeepSeekClient:
    """
    DeepSeek API 客户端类
    用于与 DeepSeek 大语言模型服务进行交互
    """

    
    def __init__(self, api_key):
        """
        初始化 DeepSeek 客户端
        :param api_key: DeepSeek API 密钥
        """
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/chat/completions"

    def generate_text(self, system_prompt, assistant_prompt="", user_prompt="", temperature=0.7, max_tokens=500, top_p=1.0, n=1):
        """
        调用 DeepSeek API 生成文本
        
        :param system_prompt: 系统提示词，用于设定AI助手的角色和行为
        :param user_prompt: 用户输入的提示词
        :param temperature: 温度参数，控制输出的随机性，
            场景	温度
            代码生成/数学解题   	0.0
            数据抽取/分析	1.0
            通用对话	1.3
            翻译	1.3
            创意类写作/诗歌创作	1.5
        :param max_tokens: 生成文本的最大标记数（单词或标点符号） 较大的值允许生成更长的回答
        :param top_p: 核采样参数，控制输出的多样性，范围0-1 控制生成内容的多样性。值越高，生成内容的词汇范围越广；值越低，生成内容的词汇范围越窄。
            创意性任务（如诗歌、故事）：使用较高的 top_p 值（如 0.8-0.9），以增加生成内容的多样性。
            确定性任务（如代码生成、问答）：使用较低的 top_p 值（如 0.3-0.5），以确保生成内容的准确性和一致性。

        :param n: 为单个提示生成的完成数量
                 通常设为1以获得单个回答
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {}
       
        # API 请求参数
        payload = {
            "model": "deepseek-chat",  # DeepSeek 对话模型
            "messages": [
                {"role": "system", "content": system_prompt},  # 系统角色设定
                {"role": "user", "content": user_prompt}       # 用户输入
            ],
            "temperature": temperature,  # 输出随机性控制
            "max_tokens": max_tokens,    # 最大生成长度
            "top_p": top_p,             # 核采样参数
            "n": n,                     # 生成答案数量
            "stream": False             # 是否启用流式输出
        }
        
        
        try:
            # 发送 POST 请求到 DeepSeek API
            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析响应并返回生成的文本
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            if hasattr(e, 'response') and e.response:
                print("错误详情：", e.response)
                print("错误详情：", e.response.text)
            return None

def save_to_file(text, file_path):
    """
    将生成的文本保存到文件
    
    :param text: 要保存的文本内容
    :param file_path: 保存文件的路径
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n\n=== 生成内容 ===\n")
            f.write(text)
            f.write("\n")
        print(f"文本已成功保存到 {file_path}")
    except IOError as e:
        print(f"文件保存失败: {e}")

# 使用示例
if __name__ == "__main__":
    # 替换为你的 API 密钥
    API_KEY = ""
    client = DeepSeekClient(API_KEY)
    
    # 设置系统提示词和用户提示词
    system_prompt = """
    你是专业的教育专家，正在作为2025年第十四届幼儿教师优秀论文征集活动的评委，对每一份作品进行评分和撰写评语，评分在0-100分之间。

    参评作品内容需要有关幼儿教育思想、理论以及教育教学、教科研、管理等领域研究与实践成果。选题务必紧密联系自身教育教学及管理工作实际情况，围绕学前教育发展进程中出现的各类问题深入展开论述。

    作品内容要具有一定的原创性、科学性和实践性；题目简练、论点鲜明、论据充足、论证严密、数据准确，文风端正、表述规范，篇幅在 3000-4000 字。

    参评内容必须为本人原创，选题得当理论与实践相结合，作品结构完整、条理清晰，体现一线幼教工作者的智慧，展现当前幼儿教育的价值取向和发展方向，并具有实践指导意义。

    此类论文为0分，并在评语中写明原因：作品非原创、抄袭率高达 70%以上或作品内容涉及小学化倾向，不符合《指南》、《纲要》精神一律为无奖作品。

    请根据以上要求，对以下作品进行评分和撰写评语。

    """

    assistant_prompt = """


    """
    user_prompt = """


    """


    # 生成文本，并设置生成参数
    response = client.generate_text(
        system_prompt=system_prompt,
        assistant_prompt=assistant_prompt,
        user_prompt=user_prompt,
        temperature=1.0,    # 较高的温度值，增加创造性
        max_tokens=8000,   # 允许生成较长的回答
        top_p=0.9,         # 适度的多样性控制
        n=1                # 生成单个回答
    )
    
    if response:
        print("生成的文本：")
        print(response)
        
        # 将生成的文本保存到文件
        save_to_file(response, "generated_texts.md")