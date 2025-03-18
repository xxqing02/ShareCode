import gradio as gr
import os
import shutil  # 用于复制文件

# 设置保存文件的目录
save_directory = "./uploads/"

# 确保保存目录存在
os.makedirs(save_directory, exist_ok=True)

# 文件上传和保存函数
def save_files(file_paths):
    for file_path in file_paths:
        # 提取原始文件名
        file_name = os.path.basename(file_path)
        # 构建目标路径
        dest_path = os.path.join(save_directory, file_name)
        # 复制文件到目标目录
        shutil.copy(file_path, dest_path)
    
    # 

    #
    return f"{len(file_paths)} 个文件已成功上传并保存到 {save_directory}"

# 创建Gradio界面
iface = gr.Interface(
    fn=save_files,
    inputs=gr.File(label="上传文件", file_count="multiple", file_types=[".xlsx", ".xls"]),
    outputs="text",
    title="Excel文件上传器",
    description="请选择多个Excel文件上传并保存到指定目录",
    flagging_mode="never"
)

# 启动Gradio界面
iface.launch()

