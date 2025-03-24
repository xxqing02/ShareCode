from openai import OpenAI
import base64,sys,os
from datetime import datetime

gpt_key = "sk-ScqGEBjwbY1mvWlcE80f2dDb45B846C5Aa218eC72a627f5d"
gpt_base = "https://apione.zen-x.com.cn/api/v1/"

client = OpenAI(api_key=gpt_key,base_url=gpt_base)

def encode_image(image_path):
    # 将图片转换为 base64 编码
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_text(example_image_path, user_image_path):
    base64_user_image = encode_image(user_image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "按照应用图标从左到右的顺序，提取游戏图标下面的白色文字(应用名)和白色文字下面的灰色文字(应用描述)。截图中可能有10个图标，请提取上面的一排游戏图标下面的信息。注意先后顺序,不要回答多余信息。"
                    },                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_user_image}",
                        }
                    }
                ]
            }
        ],
        max_tokens=1800
    )
    
    return response.choices[0].message.content


def save_result(response):
    try:
        # 获取 .exe 文件所在的目录
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 打包后的环境
            exe_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境
            exe_dir = os.getcwd()

        print(f"保存结果中: {exe_dir}")

        # 创建结果文件夹
        result_dir = os.path.join(exe_dir, "result")
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        # 生成文件名
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        txt_path = os.path.join(result_dir, f"result_{now}.txt")

        # 写入文件
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(response)

        print(f"保存结果成功: {txt_path}")
    except Exception as e:
        print(f"保存结果失败: {str(e)}")


def filter_result(result):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user", 
                "content": f"请帮我删除以下文本中的重复多余软件,并根据出现的先后顺序重新排序,只返回排名:[软件名称]:软件描述,不要回答多余信息。\n{result}"
            }
        ],
        max_tokens=1800
    )
    return response.choices[0].message.content
        
