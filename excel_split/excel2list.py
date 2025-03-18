import pandas as pd

def read_excel_to_list(file_path): # 返回一个列表，列表中的每个元素是需要分词的短句
    """
    读取 Excel 文件（.xlsx），返回每一行数据组成的字典列表
    :param file_path: Excel 文件路径
    :return: List[Dict]，每行是一个字典
    """
    try:
        df = pd.read_excel(file_path)
        rows_list = df.to_dict(orient='records')
        keywords = [item['关键词'] for item in rows_list]
        return keywords
    
    except Exception as e:
        print(f"读取 Excel 文件失败: {e}")
        return []


if __name__ == '__main__':
    # 示例调用
    file_path = 'excel_split/data.xlsx'
    data = read_excel_to_list(file_path)

    for row in data:
        print(row)