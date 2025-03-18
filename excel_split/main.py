import gradio as gr
import os
import shutil 
import glob
from excel2list import read_excel_to_list
from chater import chat
import pandas as pd

# 设置目录路径
UPLOAD_DIR = "./uploads/"
PROCESSED_DIR = "./processed/"

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

chater = chat()

# 文件上传和保存函数
def process(file_paths):
    
    for file_path in file_paths:
        # 提取原始文件名
        file_name = os.path.basename(file_path)
        # 构建目标路径
        dest_path = os.path.join(UPLOAD_DIR, file_name)
        # 复制文件到目标目录
        shutil.copy(file_path, dest_path)

    
    #找出所有的excel文件，获得里面的内容
    excel_files = glob.glob(os.path.join(UPLOAD_DIR, '*.xlsx')) + glob.glob(os.path.join(UPLOAD_DIR, '*.xls'))
    print(excel_files)  
    for file in excel_files:
        file_name = os.path.basename(file)  # 获取输入文件的文件名
        new_file_name = f"new_{file_name}"  # 在文件名中加上 'new' 后缀
        output_file = os.path.join(PROCESSED_DIR, new_file_name)
        data = read_excel_to_list(file)
        result = chater.chat_with_4o(data)
        df = pd.DataFrame({
            'Data': data,
            'Result': result
            })
        df.to_excel(output_file, index=True)
        delete_file(file)
    
    get_processed_files()
    return "Finish"

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"文件 {file_path} 已删除。")
    else:
        print(f"文件 {file_path} 不存在。")


def get_processed_files():
    # 获取处理后的文件列表（返回完整路径）
    return [os.path.join(PROCESSED_DIR, f) for f in os.listdir(PROCESSED_DIR)]

# 创建 Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("# 文件上传与下载系统")
    gr.Markdown("左边上传文件，右边下载处理后的文件")

    with gr.Row():
        # 左侧区域：文件上传和结果展示
        with gr.Column():
            file_upload = gr.File(
                label="上传 Excel 文件",
                file_count="multiple",
                file_types=[".xlsx", ".xls"]
            )
            output_text = gr.Textbox(label="上传结果", interactive=False)
            file_upload.upload(process, inputs=file_upload, outputs=output_text)

        # 右侧区域：展示处理后的文件
        with gr.Column():
            processed_files = gr.Files(
                label="处理后的文件（点击下载）",
                value=get_processed_files(),  # 直接绑定获取文件的函数
                interactive=False
            )
            

demo.launch()

