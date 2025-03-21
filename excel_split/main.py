import gradio as gr
import os
import shutil
import glob
from excel2list import read_excel_to_list
from chater import chat
import pandas as pd

# 设置目录路径
UPLOAD_DIR = "./excel_split/uploads/"
PROCESSED_DIR = "./excel_split/processed/"
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")  # 获取当前文件所在目录下的static文件夹
gr.set_static_paths("/home/zhouhan/ShareCode/excel_split/static")

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

chater = chat()

# 文件上传和保存函数
def process(file_paths, processed_files_state):
    # 清空上传目录
    for file_path in file_paths:
        # 提取原始文件名
        file_name = os.path.basename(file_path)
        # 构建目标路径
        dest_path = os.path.join(UPLOAD_DIR, file_name)
        # 复制文件到目标目录
        shutil.copy(file_path, dest_path)

    # 找出所有的excel文件，获得里面的内容
    excel_files = glob.glob(os.path.join(UPLOAD_DIR, '*.xlsx')) + glob.glob(os.path.join(UPLOAD_DIR, '*.xls'))
    print(excel_files)
    for file in excel_files:
        status = False
        while not status:
            file_name = os.path.basename(file)  # 获取输入文件的文件名
            new_file_name = f"new_{file_name}"  # 在文件名中加上 'new' 后缀
            output_file = os.path.join(PROCESSED_DIR, new_file_name)
            data, num = read_excel_to_list(file)
            result = chater.chat_with_4o(data)
            if len(data) == len(result):
                status = True
            else:
                continue
            df = pd.DataFrame({
                'Data': data,
                'Result': result
                })
            df.to_excel(output_file, index=False)
        delete_file(file)

    # 更新处理后的文件列表
    processed_files_state = get_processed_files()
    return "成功处理了 {} 行".format(num), processed_files_state

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"文件 {file_path} 已删除。")
    else:
        print(f"文件 {file_path} 不存在。")


def get_processed_files():
    # 获取处理后的文件列表（返回完整路径）
    return [os.path.join(PROCESSED_DIR, f) for f in os.listdir(PROCESSED_DIR)]


# 展示选中文件的部分处理结果
def show_partial_results(selected_file):
    if not selected_file or selected_file == "请选择文件":  # 如果没有选中文件或选择了空选项
        return None, gr.update(visible=False), gr.update(visible=False)  # 隐藏展示窗口和删除按钮
    try:
        # 读取选中的 Excel 文件
        df = pd.read_excel(selected_file)
        return df, gr.update(visible=True), gr.update(visible=True)  # 显示完整数据和删除按钮
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None, gr.update(visible=False), gr.update(visible=False)

def delete_selected_file(selected_file, processed_files_state):
    if selected_file and selected_file != "请选择文件":
        try:
            # 删除文件
            os.remove(selected_file)
            # 更新文件列表
            processed_files_state = get_processed_files()
            return "文件已删除", gr.update(choices=["请选择文件"] + processed_files_state), processed_files_state, None, gr.update(visible=False), gr.update(visible=False)
        except Exception as e:
            return f"删除文件失败: {e}", gr.update(), processed_files_state, None, gr.update(visible=False), gr.update(visible=False)
    return "请先选择要删除的文件", gr.update(), processed_files_state, None, gr.update(visible=False), gr.update(visible=False)


# 创建 Gradio 界面
with gr.Blocks() as demo:
    with gr.Column():
        gr.HTML(
        """
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="/gradio_api/file=static/icon.jpg" style="height: 32px; object-fit: contain;">
            <h1 style="margin: 0;">AI分词工具</h1>
        </div>
        """
         )
        gr.Markdown("提示:上传Excel文档后可以自动分词, 并把分词结果保存在Excel中以供下载")

    # 状态变量：存储处理后的文件列表
    processed_files_state = gr.State([])

    with gr.Row():
        # 左侧区域：文件上传和结果展示
        with gr.Column():
            file_upload = gr.File(
                label="上传 Excel 文件",
                file_count="multiple",
                file_types=[".xlsx", ".xls"]
            )
            output_text = gr.Textbox(label="处理结果", interactive=False)

            # 文件上传后触发处理函数
            file_upload.upload(
                process,
                inputs=[file_upload, processed_files_state],  # 明确指定输入参数
                outputs=[output_text, processed_files_state]  # 明确指定输出参数
            )

        # 右侧区域：展示处理后的文件
        with gr.Column():
            processed_files = gr.Files(
                label="处理后的文件（点击下载）",
                interactive=False
            )

            # 动态更新 gr.Files 的内容
            processed_files_state.change(
                lambda files: gr.update(value=files),
                inputs=processed_files_state,
                outputs=processed_files
            )

            # 添加选项框：选择处理后的文件
            file_dropdown = gr.Dropdown(
                label="选择处理后的文件",
                choices=["请选择文件"],  # 初始为空选项
                interactive=True
            )

            # 添加展示窗口：展示选中文件的处理结果（带分页）
            partial_results_display = gr.Dataframe(
                label="处理结果",
                interactive=False,
                visible=False,  # 初始状态为隐藏
                row_count=10,   # 每页显示10行
                wrap=True      # 允许内容换行
            )

            # 添加删除按钮
            delete_button = gr.Button("删除选中文件", visible=False)

            # 动态更新选项框的内容
            processed_files_state.change(
                lambda files: gr.update(choices=["请选择文件"] + files),  # 增加空选项
                inputs=processed_files_state,
                outputs=file_dropdown
            )

            # 选项框选择文件后，展示部分处理结果，并控制展示窗口的可见性
            file_dropdown.change(
                show_partial_results,
                inputs=file_dropdown,
                outputs=[partial_results_display, partial_results_display, delete_button]
            )

            # 删除按钮点击事件
            delete_button.click(
                delete_selected_file,
                inputs=[file_dropdown, processed_files_state],
                outputs=[output_text, file_dropdown, processed_files_state, partial_results_display, partial_results_display, delete_button]
            )

demo.launch(server_name='0.0.0.0', server_port=7860, allowed_paths=['./'])
