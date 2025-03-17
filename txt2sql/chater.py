import openai
from key import *
from retriever import Retriever  
import re

class chat:
    def __init__(self):
        self.client = openai.OpenAI(api_key=gpt_key, base_url=gpt_base)
        self.prompt = None
        self.query_select = Retriever()
        
    def chat_with_4o(self, message, prompt): # 根据输入生成SQL
        try:
            response = self.client.chat.completions.create(
                
                # model="qwen-plus",
                
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1024,
                temperature=0.7,
                top_p=1.0,
                n=1,
                stop=None
            )
            sql_result = response.choices[0].message.content.strip()
            return sql_result
        except Exception as e:
            return f"❌ OpenAI 生成 SQL 失败：{e}"

    def natural_language_query(self, nl_query):
        table_and_field = self.query_select.get_tables_and_fields()  # 获取表和字段
        chatbot_prompt,status = self.query_select.generate_dynamic_prompt(table_and_field)
        sql_suggestion = self.chat_with_4o(nl_query, chatbot_prompt)
        print(f"SQL Suggestion: {sql_suggestion}")
        if status: # 如果生成SQL成功
            sql_suggestion = self.extract_sql(sql_suggestion)  # 从回复的代码块中提取SQL ```sql{reply SQL}```
            print(f"SQL Suggestion(extracted): {sql_suggestion}")
            query_result = self.query_select.sql_query(sql_suggestion) # 执行SQL返回结果

            if query_result:
                headers = query_result[0].keys() if isinstance(query_result[0], dict) else []
                rows = [[row[col] for col in headers] for row in query_result]
                md_table = "| " + " | ".join(headers) + " |\n"
                md_table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                for row in rows:
                    md_table += "| " + " | ".join(str(cell) for cell in row) + " |\n"

                return sql_suggestion, md_table
            else:
                return sql_suggestion, "⚠️ 没有查询到数据或执行失败！"
        else:
            return sql_suggestion, "❌ 生成SQL失败！"

    @staticmethod
    def extract_sql(text):
        sql_matches = re.findall(r"```sql\s*(.*?)\s*```", text, re.DOTALL)
        if sql_matches:
            return sql_matches[0].strip() 
        else:
            return text


