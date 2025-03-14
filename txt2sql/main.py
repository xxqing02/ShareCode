import gradio as gr
from chater import chat
from file_importer import file_importer

if __name__ == "__main__":

    importer = file_importer()
    chater = chat()

    with gr.Blocks(title="自然语言 SQL 查询系统") as demo:
        gr.Markdown("# 📝 自然语言数据库查询助手")
        gr.Markdown("### 输入自然语言查询需求，系统自动生成 SQL 并查询数据库\n### 或上传 Excel 文件导入数据库")
        with gr.Row():
            nl_input = gr.Textbox(label="自然语言查询", placeholder="例如：查询所有管理员的用户名")
            search_btn = gr.Button("🔍 查询")

        with gr.Row():
            sql_output = gr.Textbox(label="生成的SQL语句", lines=3)
            query_result_output = gr.Markdown(label="查询结果")

        search_btn.click(fn=chater.natural_language_query, inputs=[nl_input], outputs=[sql_output, query_result_output])

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

    demo.launch(server_name="127.0.0.1", server_port=7860)