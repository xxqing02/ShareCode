import os
import gradio as gr
import tempfile
import shutil


def generate_file(file_objs):  # 参数变为文件对象列表
    global tmpdir
    output_paths = []
    
    for file_obj in file_objs:  # 遍历每个文件
        try:
            # 获取原始文件名
            original_name = os.path.basename(file_obj.name)
            
            # 生成新文件名（添加"New"前缀）
            new_name = "New" + original_name
            
            # 创建新文件完整路径
            output_path = os.path.join(tmpdir, new_name)
            
            # 直接读取上传文件内容并写入新文件
            with open(file_obj.name, 'rb') as src_file:  # 修改点1：使用不同变量名
                with open(output_path, 'wb') as dst_file:
                    shutil.copyfileobj(src_file, dst_file)  # 修改点2：更高效的文件复制方式
                    
            output_paths.append(output_path)  # 收集所有生成的新路径
            
        except Exception as e:
            print(f"文件 {file_obj.name} 处理失败: {str(e)}")
            continue  # 修改点3：跳过错误文件继续处理
    
    return output_paths  # 返回所有成功生成的文件路径
    
    

def main():
    global tmpdir
    with tempfile.TemporaryDirectory(dir='.') as tmpdir:
        # 定义输入和输出
        inputs = gr.components.File(label="上传文件", file_count="multiple") 
        outputs = gr.components.File(label="下载文件",file_count="multiple")  

        app = gr.Interface(fn=generate_file, inputs=inputs, outputs=outputs,   title="文件上传、并生成可下载文件demo",
                      description="上传任何文件都可以，只要大小别超过你电脑的内存即可"
      )

        app.launch()

main()

