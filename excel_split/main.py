import gradio as gr
import os
import shutil
import glob
from excel2list import read_excel_to_list
from chater import chat
import pandas as pd
from prompt import prompt

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

def parse_prompt_examples(prompt_text):
    """解析prompt中的示例"""
    examples = []
    lines = prompt_text.split('\n')
    for line in lines:
        if '分词之前:' in line and '分词之后:' in line:
            before = line.split('分词之前:')[1].split('分词之后:')[0].strip()
            after = line.split('分词之后:')[1].strip()
            examples.append((before, after))
    return examples

def format_prompt_examples(examples):
    """将示例格式化为prompt文本"""
    prompt_text = "你是一个中文分词专家。请对以下句子进行分词，每个词之间用空格分隔，保留原有顺序。\n"
    prompt_text += "只返回分词后的文本，不要解释，不要输出多余内容, 严格按照例子给出的格式输出,下面是一些例子: \n"
    for before, after in examples:
        prompt_text += f"分词之前: {before}  分词之后: {after}\n"
    return prompt_text

def validate_examples(before_examples, after_examples):
    """验证示例是否有效"""
    # 检查左右是否对应
    if len(before_examples) != len(after_examples):
        return False, "左右示例数量必须相同"
    
    # 检查是否有非空值
    has_valid_example = False
    for i in range(len(before_examples)):
        # 如果一对值都为空，则跳过
        if not before_examples[i] and not after_examples[i]:
            continue
        # 如果只有一个为空，则报错
        if not before_examples[i] or not after_examples[i]:
            return False, f"第{i+1}行示例必须同时为空或同时有值"
        has_valid_example = True
    
    if not has_valid_example:
        return False, "请至少提供一个有效的示例"
    
    return True, "验证通过"

def preview_prompt(before_examples, after_examples):
    """预览prompt"""
    is_valid, message = validate_examples(before_examples, after_examples)
    if not is_valid:
        return message, None
    
    # 过滤掉空值对
    examples = [(b, a) for b, a in zip(before_examples, after_examples) if b and a]
    new_prompt = format_prompt_examples(examples)
    
    return "示例验证通过", new_prompt

# 文件上传和保存函数
def process(file_paths, processed_files_state, batch_size):
    if not file_paths:
        return "请先上传文件", processed_files_state
        
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
            
            # 读取所有数据
            data, total_rows = read_excel_to_list(file)
            
            # 分批处理数据
            all_results = []
            for i in range(0, len(data), batch_size):
                batch_data = data[i:i + batch_size]
                result = chater.chat_with_4o(batch_data)
                all_results.extend(result)
                
                # 更新进度
                progress = min(100, int((i + batch_size) / len(data) * 100))
                yield f"正在处理: {progress}%", processed_files_state
            
            if len(data) == len(all_results):
                status = True
            else:
                continue
                
            df = pd.DataFrame({
                'Data': data,
                'Result': all_results
            })
            df.to_excel(output_file, index=False)
            
            # 更新处理后的文件列表
            processed_files_state = get_processed_files()
            yield f"成功处理了 {total_rows} 行", processed_files_state
            
        delete_file(file)

    return "处理完成", processed_files_state

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
        # 左侧区域：文件上传和示例编辑
        with gr.Column():
            file_upload = gr.File(
                label="上传 Excel 文件",
                file_count="multiple",
                file_types=[".xlsx", ".xls"]
            )

            # 添加prompt编辑区域
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 分词示例编辑")
                    before_examples = []
                    after_examples = []
                    
                    # 从原始prompt中解析示例
                    original_examples = parse_prompt_examples(prompt)
                    
                    # 创建5个示例的输入框
                    for i in range(5):
                        with gr.Row():
                            before = gr.Textbox(
                                label=f"分词之前 {i+1}",
                                value=original_examples[i][0] if i < len(original_examples) else "",
                                placeholder="输入原始文本"
                            )
                            after = gr.Textbox(
                                label=f"分词之后 {i+1}",
                                value=original_examples[i][1] if i < len(original_examples) else "",
                                placeholder="输入分词结果"
                            )
                            before_examples.append(before)
                            after_examples.append(after)
                    
                    # 添加预览按钮
                    preview_button = gr.Button("预览示例", variant="primary")
                    prompt_status = gr.Textbox(label="验证状态", interactive=False)
                    prompt_preview = gr.Textbox(label="示例预览", interactive=False, lines=5)
                    
                    # 预览按钮点击事件
                    def preview_examples(*args):
                        # 分离前后示例
                        n = len(args) // 2
                        before = args[:n]
                        after = args[n:]
                        return preview_prompt(before, after)
                    
                    preview_button.click(
                        preview_examples,
                        inputs=before_examples + after_examples,
                        outputs=[prompt_status, prompt_preview]
                    )

        # 右侧区域：处理控制和结果展示
        with gr.Column():
            # 添加处理控制区域
            with gr.Row():
                with gr.Column():
                    # 添加滑动条
                    batch_size = gr.Slider(
                        minimum=1,
                        maximum=100,  # 默认最大值，会根据实际文件行数动态调整
                        value=10,     # 默认值
                        step=1,
                        label="每次处理的行数"
                    )
                    
                    # 添加开始处理按钮
                    start_button = gr.Button("开始处理", variant="primary")
                    
                    output_text = gr.Textbox(label="处理结果", interactive=False)

            # 当文件上传后，更新滑动条的最大值
            def update_slider_max(file_paths):
                if not file_paths:
                    return gr.update(maximum=100)
                # 读取第一个文件的行数
                data, row_count = read_excel_to_list(file_paths[0])
                return gr.update(maximum=max(1, row_count))
            
            file_upload.change(
                update_slider_max,
                inputs=file_upload,
                outputs=batch_size
            )
            
            # 开始处理按钮点击事件
            start_button.click(
                process,
                inputs=[file_upload, processed_files_state, batch_size],
                outputs=[output_text, processed_files_state]
            )

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
