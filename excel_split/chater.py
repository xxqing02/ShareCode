import openai
from key import *
from prompt import prompt


from excel2list import read_excel_to_list

class chat:
    def __init__(self):
        self.client = openai.OpenAI(api_key=gpt_key, base_url=gpt_base)
        self.prompt = prompt
        
    def chat_with_4o(self, excel_input): # 输入excel的每一行数据和prompt
        try:
            message = ""
            for idx, sentence in enumerate(excel_input, 1):
                message += f"{idx}. {sentence}\n"

            response = self.client.chat.completions.create(
                               
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1024,
                temperature=0.7,
                top_p=1.0,
                n=1,
                stop=None
            )
            result = response.choices[0].message.content
            return result
        except Exception as e:
            return f"❌ OpenAI 生成 SQL 失败：{e}"
        
if __name__ == '__main__':
    # 示例调用
    chater = chat()
    file_path = 'excel_split/data.xlsx'
    data = read_excel_to_list(file_path)
    result = chater.chat_with_4o(data)
    print(result)

