# receive all the tables and fields, and generate the max possibility of the tables and fields which will be used according to 
# the input of user
import openai
from key import *
from retriever import Retriever

class Prompter:
    def __init__(self):
        self.client = openai.OpenAI(api_key=gpt_key, base_url=gpt_base)
        
    def _predict_schema(self, user_input, table_field_map):
        """
        根据用户输入预测和数据库中全部的表和字段，预测本次查询中最可能使用的表和字段
        
        Args:   
            user_input (str): 用户的自然语言输入
            table_field_map (dict): 数据库中的表和字段
            
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
                max_tokens=2048,
                temperature=0.3,
                top_p=1.0,
                n=1
            )
            
            # 解析预测结果
            prediction = response.choices[0].message.content.strip()
            return prediction
            
        except Exception as e:
            print(f"预测表和字段失败：{e}")
            return [], []
            
    def _build_prediction_prompt(self, user_input, table_field_map):
        prompt = """你是一个数据库专家，需要根据用户的自然语言输入预测本次查询中最可能使用的数据库表和字段。
        
        数据库包含以下表和字段：
        """
        for table, fields in table_field_map.items():
            prompt += f"\n表名:{table}\n字段:{', '.join(fields)}\n"
            
        prompt += """
        
        请根据用户的输入,预测最可能使用的表和字段.请以JSON格式返回结果,格式如下:
        {
            "possible_tables": ["table1", "table2"],
            "possible_fields": {
                "table1": ["field1", "field2"],
                "table2": ["field3"]
            }
        }
        只返回JSON格式的结果，不要包含其他文字。
        """
        return prompt
        
        
if __name__ == "__main__":
    prompter = Prompter()
    retriever = Retriever()
    table_field_map = retriever.get_tables_and_fields()
    prediction = prompter._predict_schema("查询所有用户的订单", table_field_map)
    print(prediction)