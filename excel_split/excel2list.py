import pandas as pd

import pandas as pd

def read_excel_to_list(file_path):
    """
    读取 Excel 文件（.xlsx），返回第一列数据组成的列表，跳过第一行
    :param file_path: Excel 文件路径
    :return: List，第一列的数据列表
    """
    try:
        # 读取 Excel 文件，跳过第一行
        df = pd.read_excel(file_path)
        
        # 获取第一列数据并转换为列表
        first_column = df.iloc[:, 0].tolist()

        row_count = len(first_column)
        return first_column, row_count
    
    except Exception as e:
        print(f"读取 Excel 文件失败: {e}")
        return []



if __name__ == '__main__':
    # 示例调用
    file_path = 'excel_split/data.xlsx'
    data ,row_count= read_excel_to_list(file_path)

    for row in data:
        print(row)