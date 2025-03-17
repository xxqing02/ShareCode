# receive all the tables and fields, and generate the max possibility of the tables and fields which will be used according to 
# the input of user

import openai
from key import *

class Prompter:
    def __init__(self):
        self.client = openai.OpenAI(api_key=gpt_key, base_url=gpt_base)
        
    def predict_tables_and_fields(self, user_input, table_field_map):
        """
        根据用户输入预测最可能使用的表和字段
        
        Args:
            user_input (str): 用户的自然语言输入
            table_field_map (dict): 数据库中的表和字段映射
            
        Returns:
            tuple: (预测的表列表, 预测的字段列表)
        """
        try:
            # 构建提示词
            prompt = self._build_prediction_prompt(user_input, table_field_map)
            
            # 调用GPT模型进行预测
            response = self.client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=512,
                temperature=0.3,
                top_p=1.0,
                n=1
            )
            
            # 解析预测结果
            prediction = response.choices[0].message.content.strip()
            predicted_tables, predicted_fields = self._parse_prediction(prediction, table_field_map)
            
            return predicted_tables, predicted_fields
            
        except Exception as e:
            print(f"❌ 预测表和字段失败：{e}")
            return [], []
            
    def _build_prediction_prompt(self, user_input, table_field_map):
        """构建预测提示词"""
        prompt = """你是一个数据库专家，需要根据用户的自然语言输入预测最可能使用的数据库表和字段。
        
        数据库包含以下表和字段：
        """
        # 添加表和字段信息
        for table, fields in table_field_map.items():
            prompt += f"\n表名：{table}\n字段：{', '.join(fields)}\n"
            
        prompt += """
        请根据用户的输入，预测最可能使用的表和字段。请以JSON格式返回结果，格式如下：
        {
            "tables": ["表1", "表2"],
            "fields": ["字段1", "字段2"]
        }

        只返回JSON格式的结果，不要包含其他文字。"""
        return prompt
        
    def _parse_prediction(self, prediction, table_field_map):
        """解析预测结果"""
        import json
        try:
            result = json.loads(prediction)
            predicted_tables = [table for table in result.get("tables", []) 
                              if table in table_field_map]
            predicted_fields = [field for field in result.get("fields", []) 
                              if any(field in fields for fields in table_field_map.values())]
            return predicted_tables, predicted_fields
        except:
            return [], []


