import openai
from key import api_key, base

from query_select import Retriever  # 你之前写的数据库查询方法
from file_importer import file_importer  # 将excel存入mysql


class chat:
    def __init__(self):
        self.client = openai.OpenAI(api_key=api_key, base_url=base)
        self.prompt = None
        self.query_select = Retriever()
        

    # OpenAI 调用逻辑（生成 SQL）
    def chat_with_4o(self, message, prompt):
        try:
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
        
        table_and_field = self.query_select.get_tables_and_fields()
        chatbot_prompt = self.query_select.generate_dynamic_prompt(table_and_field)
        sql_suggestion = self.chat_with_4o(nl_query, chatbot_prompt)

        # 2. 执行 SQL 查询
        query_result = self.query_select.sql_query(sql_suggestion)

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

    def generate_dynamic_prompt(self, table_field_map):
        prompt_header = (
            "你是一个文本转SQL的生成器,你的主要任务是尽可能协调客户,将输入的文本转换成正确的SQL语句。\n"
            "上下文开始\n"
            "表名和表字段来自下表:\n"
        )

        table_descriptions = ""
        for table, fields in table_field_map.items():
            field_list = ",".join(fields)
            table_descriptions += f"表名:{table}\n字段:{field_list}\n\n"

        # example_prompt = (
        #     "请按照以下样例为客户进行回复:\n"
        #     "问:请帮我查询所有的用户信息\n"
        #     f"答:SELECT * FROM {list(table_field_map.keys())[0]}\n"
        #     "问:请帮我查询所有的用户信息的姓名\n"
        #     f"答:SELECT {table_field_map[list(table_field_map.keys())[0]][0]} FROM {list(table_field_map.keys())[0]}\n"
        # )
        example_prompt = "请按照以下样例为客户进行回复:" \
        "问:请帮我查询所有的用户信息" \
        "答:SELECT * FROM User;" \
        "问:请帮我查询所有的用户信息的姓名" \
        "答:SELECT name FROM User;"

        return prompt_header + table_descriptions + example_prompt
