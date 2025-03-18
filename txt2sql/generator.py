# 根据prompter生成的prompt，生成sql语句

import openai
from key import *

class Generator:    
    def __init__(self):
        self.client = openai.OpenAI(api_key=gpt_key, base_url=gpt_base)
        
    def generate_sql(self, status, user_input, prompt_json):
        """
        根据prompt生成sql语句
        
        Args:
            status (bool): 用于判断上一个大模型正常输出
            prompt_json (str): 提取到的可能用到的外键关系和表字段信息
            user_input (str): 用户的自然语言输入
            
        Returns:
            sql (str): 生成的sql语句
        """
        
        try:
            if status:
                response = self.client.chat.completions.create(
                    model='gpt-4o',
                    messages=[
                        {"role": "system", "content": prompt_json},
                        {"role": "user", "content": user_input}

                    ],
                    max_tokens=512,
                    temperature=0.3,
                    top_p=1.0,
                    n=1
                )
                sql = response.choices[0].message['content']
                status = True

            else:
                sql = None
                status = False
            return sql, status
            
        except Exception as e:
            sql = None
            status = False            
            print(f"❌ generator 模块调用失败：{e}")
            return sql, status

