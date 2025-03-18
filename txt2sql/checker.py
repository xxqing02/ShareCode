import openai
from key import * 

class Checker:
    def __init__(self):
        self.client = openai.OpenAI(api_key=gpt_key, base_url=gpt_base)
        
    def predict_tables_and_fields(self, status, user_input, sql_input):
        """
        根据用户输入预测最可能使用的表和字段，并检查生成的SQL语句是否冗余，进行优化。
        
        Args:
            status (bool): 用于判断上一个大模型正常输出
            user_input (str): 用户的自然语言输入
            sql_input (str): 来自 generator 生成的sql语句
            
        Returns:
            sql (str): 优化后的SQL语句
        """
        try:
            # 构建提示词
            prompt = self._build_prediction_prompt(status, user_input, sql_input)
            
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
            sql = response.choices[0].message.content.strip()
            
            return sql
            
        except Exception as e:
            print(f"❌ checker 模块调用失败：{e}")
            return []

    def _build_prediction_prompt(self, status, user_input, sql_input):
        """构建预测提示词"""
        
        if status:
            prompt = f"""
            You are a database expert. Your task is to check whether the generated SQL statement contains any redundancy based on the user's input. 
            If there is redundancy, you should optimize the SQL by removing the unnecessary parts.
            
            User's input: "{user_input}"
            Generated SQL statement: "{sql_input}"
            Please return the optimized SQL statement.
            """
        else:
            prompt = f"""
            Please return an error message stating that no relevant SQL can be generated.
            """
            
        return prompt
    
if __name__ == "__main__":
    checker = Checker()
    status = True
    user_input = "Find the total number of orders for each customer."
    sql_input = "SELECT customer_id, email , COUNT(order_id) AS total_orders FROM orders GROUP BY customer_id"
    print(checker.predict_tables_and_fields(status, user_input, sql_input))
