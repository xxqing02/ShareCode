import gradio as gr
from file_importer import file_importer
from prompter import Prompter
from generator import Generator
from checker import Checker
from retriever import Retriever
import pandas as pd

predefined_queries = [
    "查询所有用户的用户名和注册日期",  # 单表查询
    "查询库存少于 20 件的商品和它们的库存数量",  # 条件查询
    "查找 2024 年 1 月之后创建的所有订单信息",  # 日期条件查询
    "查询所有购买过 'iPhone 14' 的用户姓名（去重）",  # 关联查询
    "查询每个用户在所有订单中的累计消费金额",  # 分组统计
    "查询所有单价超过 5000 元的订单商品信息",  # 数值条件查询
    "查询被购买次数最多的商品及其销售数量",  # 统计查询
    "查询从未下过订单的用户姓名",  # 关联排除查询
    "查询每个月的订单数量和订单总金额，按月份升序排列",  # 时间分组统计
    "查询所有购买过 'AirPods Pro' 的用户，以及他们累计购买了多少件",  # 关联统计查询
    "查询每个用户购买的商品类别数量，并按类别数量从高到低排序。",
    "查询过去 6 个月的销售总额，即使某个月没有订单也要显示为 0",
    "查询每个用户下的订单中价格最高的商品及其价格",
    "计算每个用户两次下单之间的平均时间间隔（天），并按间隔天数升序排列",
    "查询销售额最高的商品类别，并计算该类别的总销售额"
    ]


importer = file_importer()

def query_from_excel(nl_query):
    prompter = Prompter()
    generator = Generator()
    checker = Checker()
    retriever = Retriever()
    table_and_field,retriever_status = retriever.get_tables_and_fields()  # 获取表和字段
    prediction,prompter_status = prompter._predict_schema(retriever_status,nl_query, table_and_field)
    # print(prediction)
    sql_suggestion,generator_status = generator.generate_sql(prompter_status,nl_query,prediction)
    # print(sql_suggestion)
    sql_result,checker_status = checker.check_sql(generator_status,nl_query,sql_suggestion)
    query_result= retriever.sql_query(sql_result)
    print("查询结果：",query_result)
    query_result = sql_result_to_html(query_result)
    return  sql_result, query_result

def sql_result_to_html(sql_result):
    """将 SQL 查询结果转换为 HTML 表格，并添加样式"""
    if isinstance(sql_result, pd.DataFrame):
        table_html = sql_result.to_html(index=False, escape=False)  # 生成 HTML 表格
    elif isinstance(sql_result, list):
        if not sql_result:
            return "<p>查询无结果</p>"
        headers = sql_result[0].keys()
        rows = [list(row.values()) for row in sql_result]
        df = pd.DataFrame(rows, columns=headers)
        table_html = df.to_html(index=False, escape=False)
    else:
        return "<p>查询结果格式不支持</p>"

    # 自定义表格样式
    # 灰白风格表格样式
    style = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
            background-color: #f8f8f8; /* 淡灰背景 */
            color: #333; /* 深灰色文字 */
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1); /* 轻微阴影 */
            border-radius: 8px;
            overflow: hidden;
        }
        th {
            background-color: #666; /* 深灰色表头 */
            color: white;
            padding: 10px;
            text-align: center;
        }
        td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }
        tr:nth-child(even) {
            background-color: #eee; /* 斑马纹（浅灰色） */
        }
        tr:hover {
            background-color: #ddd; /* 鼠标悬停时的颜色 */
        }
    </style>
    """
    return style + table_html
    

if __name__ == "__main__":

    with gr.Blocks(title="自然语言 SQL 查询系统") as demo:
        gr.Markdown("# 📝 自然语言数据库查询助手")
        gr.Markdown("### 输入自然语言查询需求，系统自动生成 SQL 并查询数据库\n### 或上传 Excel 文件导入数据库")

        with gr.Row():
            nl_input = gr.Dropdown(
                label="自然语言查询",
                choices=predefined_queries,
                allow_custom_value=True,  # 允许用户输入自定义查询
                interactive=True
            )

            search_btn = gr.Button("🔍 查询")

        with gr.Row():
            sql_result = gr.Textbox(label="生成的SQL语句", lines=3)
            query_result = gr.HTML(label="查询结果")

        search_btn.click(fn=query_from_excel, inputs=[nl_input], outputs=[sql_result, query_result])

        gr.Markdown("---")
        gr.Markdown("### 📥 Excel 文件上传导入数据库")
        with gr.Row():
            file_input = gr.File(label="📤 上传 Excel 文件", file_types=[".xlsx", ".xls"], file_count="multiple")
            upload_btn = gr.Button("🚀 导入到数据库")

        upload_result_output = gr.Textbox(label="导入结果", lines=2)
        upload_btn.click(
            fn=lambda files: importer.import_multiple_excels_to_mysql([file.name for file in files]),
            inputs=[file_input],
            outputs=[upload_result_output]
        )

    demo.launch(server_name="0.0.0.0", server_port=7860)

    # python txt2sql\main.py --server_name 0.0.0.0 --server_port 7860
