import openai
from key import api_key, base

from query_select import execute_query_direct  # 你之前写的数据库查询方法
from file_importer import file_importer  # 将excel存入mysql


class chat:
    def __init__(self):
        self.client = openai.OpenAI(api_key=api_key, base_url=base)
        self.file_importer = file_importer()

    # OpenAI 调用逻辑（生成 SQL）
    def chat_with_4o(self, message, prompt):
        try:
            print(message,'message')
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=150,
                temperature=0.7,
                top_p=1.0,
                n=1,
                stop=None
            )
            sql_result = response.choices[0].message.content.strip()
            return sql_result
        except Exception as e:
            return f"❌ OpenAI 生成 SQL 失败：{e}"

    # 整体查询逻辑
    def natural_language_query(self, nl_query):
        # 1. 自然语言转 SQL
        chatbot_prompt = self.file_importer.chatbot_prompt
        sql_suggestion = self.chat_with_4o(nl_query, chatbot_prompt)
        print(sql_suggestion,'sql')

        # 2. 执行 SQL 查询
        query_result = execute_query_direct(sql_suggestion)

        # 3. 格式化展示
        if query_result:
            # 拼接表格显示
            headers = query_result[0].keys() if isinstance(query_result[0], dict) else []
            rows = [[row[col] for col in headers] for row in query_result]
            
            # 用 Markdown 表格返回
            md_table = "| " + " | ".join(headers) + " |\n"
            md_table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
            for row in rows:
                md_table += "| " + " | ".join(str(cell) for cell in row) + " |\n"

            return sql_suggestion, md_table
        else:
            return sql_suggestion, "⚠️ 没有查询到数据或执行失败！"


