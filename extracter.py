from openai import OpenAI
import base64,sys,os
from datetime import datetime
gpt_key = "sk-79e4a8df9ad2481f99c702dd2fe38a27"
gpt_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"

client = OpenAI(
    api_key=gpt_key,
    base_url=gpt_base
)

def save_path(relative_path):
    """ 获取资源文件的绝对路径 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 会将资源文件解压到 _MEIPASS 目录
        base_path = sys._MEIPASS
    else:
        # 开发环境中的路径
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def encode_image(image_path):
    """将图片转换为 base64 编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_text(example_image_path, user_image_path):
    # 转换示例图片和用户图片为 Base64 编码
    base64_example_image = encode_image(example_image_path)
    base64_user_image = encode_image(user_image_path)

    # 构建 messages
    response = client.chat.completions.create(
        model="qwen-vl-plus",
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
    # 返回模型的响应内容
    return response.choices[0].message.content

# utf-8编码 
def save_result(response):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    txt_path = save_path(f"result/result_{now}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(response)

def filter_result(result):
    #输入的result可能有重复元素，让大模型删除多余的内容
    response = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {
                "role": "user", 
                "content": f"请帮我删除以下文本中的重复多余游戏名称，并根据游戏出现的先后顺序重新排序,选出top50个游戏:\n{result}"
            }
        ],
        max_tokens=1800
    )
    return response.choices[0].message.content
        

if __name__ == "__main__":
    image_path = "photo/example.png" 
    image_path2="photo/rank0.png"
    result=extract_text(image_path,image_path2)
    print(result)
    save_result(result)
