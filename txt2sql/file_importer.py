import pandas as pd
import mysql.connector
from mysql.connector import Error

class file_importer:
    def __init__(self):
        self.db_config = {
        'host': '192.168.10.232',
        'port': 3306,
        'user': 'zhtest',
        'password': 'Zenx_2eetheeT6',
        'database': 'zhtest'
        }
        self.chatbot_prompt = None
        self.table_field_map = {}
        
    def import_excel_to_mysql(self, file_path):
        try:
            print(file_path,'path')
            xls = pd.ExcelFile(file_path)
            sheets = xls.sheet_names
            print(f"📄 发现 {len(sheets)} 个 sheet：{sheets}")

            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()


            for sheet in sheets:
                df = pd.read_excel(xls, sheet_name=sheet)
                table_name = sheet.strip().replace(" ", "_")

                # 记录表名和字段名
                self.table_field_map[table_name] = list(df.columns)

                create_table_sql = self.generate_create_table_sql(table_name, df)
                print(f"🛠️ 正在创建表：{table_name}")
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                cursor.execute(create_table_sql)

                for _, row in df.iterrows():
                    insert_sql = self.generate_insert_sql(table_name, df.columns)
                    cursor.execute(insert_sql, tuple(row))

            connection.commit()
            cursor.close()
            connection.close()

            # 生成prompt
            self.chatbot_prompt = self.generate_dynamic_prompt(self.table_field_map)
            print('prompt', self.chatbot_prompt)

            return f"✅ 成功导入 {len(sheets)} 个 sheet 到数据库！"

        except mysql.connector.Error as e:
            return f"❌ 导入失败：{e}"


    def generate_create_table_sql(self, table_name, df):
        sql = f"CREATE TABLE {table_name} ("
        for col in df.columns:
            sql += f"`{col}` TEXT NULL,"  # 简单处理，默认 TEXT 类型
        sql = sql.rstrip(",") + ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
        return sql

    def generate_insert_sql(self, table_name, columns):
        col_names = ", ".join([f"`{col}`" for col in columns])
        placeholders = ", ".join(["%s"] * len(columns))
        sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
        return sql


    def generate_dynamic_prompt(self, table_field_map):
        prompt_header = (
            "你是一个文本转SQL的生成器,你的主要任务是尽可能协调客户,将输入的文本转换成正确的SQL语句。\n"
            "上下文开始\n"
            "表名和表字段来自下表:\n"
        )

        table_descriptions = ""
        for table, fields in table_field_map.items():
            field_list = ",".join(fields)
            table_descriptions += f"表名:{table}\n字段:{field_list}\n\n"

        example_prompt = (
            "请按照以下样例为客户进行回复:\n"
            "问:请帮我查询所有的用户信息\n"
            f"答:SELECT * FROM {list(table_field_map.keys())[0]}\n"
            "问:请帮我查询所有的用户信息的姓名\n"
            f"答:SELECT {table_field_map[list(table_field_map.keys())[0]][0]} FROM {list(table_field_map.keys())[0]}\n"
        )

        return prompt_header + table_descriptions + example_prompt