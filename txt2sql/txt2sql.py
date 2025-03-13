import gradio as gr
import openai
from key import api_key, base
from prompt import chatbot_prompt

from execute_query import execute_query_direct  # 你之前写的数据库查询方法
from file_importer import import_excel_to_mysql

# 初始化 OpenAI 客户端
client = openai.OpenAI(api_key=api_key, base_url=base)

# OpenAI 调用逻辑（生成 SQL）
def chat_with_4o(message, prompt):
    try:
        response = client.chat.completions.create(
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
def natural_language_query(nl_query):
    # 1. 自然语言转 SQL
    sql_suggestion = chat_with_4o(nl_query, chatbot_prompt)

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

def handle_file_upload(file):
    if file is None:
        return "⚠️ 请先上传文件"
    return import_excel_to_mysql(file.name)

with gr.Blocks(title="自然语言 SQL 查询系统") as demo:
    gr.Markdown("# 📝 自然语言数据库查询助手")
    gr.Markdown("### 输入自然语言查询需求，系统自动生成 SQL 并查询数据库\n### 或上传 Excel 文件导入数据库")

    # 自然语言查询模块
    with gr.Row():
        nl_input = gr.Textbox(label="自然语言查询", placeholder="例如：查询所有管理员的用户名")
        search_btn = gr.Button("🔍 查询")

    with gr.Row():
        sql_output = gr.Textbox(label="生成的SQL语句", lines=3)
        query_result_output = gr.Markdown(label="查询结果")

    search_btn.click(fn=natural_language_query, inputs=[nl_input], outputs=[sql_output, query_result_output])

    gr.Markdown("---")

    # Excel导入模块
    gr.Markdown("### 📥 Excel 文件上传导入数据库")
    with gr.Row():
        file_input = gr.File(label="📤 上传 Excel 文件", file_types=[".xlsx", ".xls"])
        upload_btn = gr.Button("🚀 导入到数据库")

    upload_result_output = gr.Textbox(label="导入结果", lines=2)
    upload_btn.click(fn=handle_file_upload, inputs=[file_input], outputs=[upload_result_output])

demo.launch(server_name="0.0.0.0", server_port=7860)

