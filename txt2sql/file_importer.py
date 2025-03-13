import pandas as pd
import mysql.connector
from mysql.connector import Error

# MySQL连接配置
db_config = {
    'host': '192.168.10.232',
    'port': 3306,
    'user': 'zhtest',
    'password': 'Zenx_2eetheeT6',
    'database': 'zhtest'
}

def import_excel_to_mysql(file_path):
    try:
        # 读取所有 Sheet
        xls = pd.ExcelFile(file_path)
        sheets = xls.sheet_names
        print(f"📄 发现 {len(sheets)} 个 sheet：{sheets}")

        # 连接数据库
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        for sheet in sheets:
            df = pd.read_excel(xls, sheet_name=sheet)
            table_name = sheet.strip().replace(" ", "_")  # 表名来自 sheet 名，去空格

            # 生成建表SQL
            create_table_sql = generate_create_table_sql(table_name, df)
            print(f"🛠️ 正在创建表：{table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            cursor.execute(create_table_sql)

            # 插入数据
            for _, row in df.iterrows():
                insert_sql = generate_insert_sql(table_name, df.columns)
                cursor.execute(insert_sql, tuple(row))

        connection.commit()
        cursor.close()
        connection.close()

        return f"✅ 成功导入 {len(sheets)} 个 sheet 到数据库！"

    except Error as e:
        return f"❌ 导入失败：{e}"

def generate_create_table_sql(table_name, df):
    sql = f"CREATE TABLE {table_name} ("
    for col in df.columns:
        sql += f"`{col}` TEXT,"  # 简单处理，默认 TEXT 类型
    sql = sql.rstrip(",") + ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
    return sql

def generate_insert_sql(table_name, columns):
    col_names = ", ".join([f"`{col}`" for col in columns])
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
    return sql
