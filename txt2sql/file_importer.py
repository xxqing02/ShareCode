import pandas as pd
import mysql.connector

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

    def import_multiple_excels_to_mysql(self, file_paths):
        success_files = []
        failed_files = []

        for file_path in file_paths:
            print(f"📂 正在处理文件: {file_path}")
            try:
                result = self.import_excel_to_mysql(file_path)
                print(result)
                success_files.append(file_path)
            except Exception as e:
                print(f"⚠️ 文件 {file_path} 处理失败: {e}")
                failed_files.append((file_path, str(e)))

        msg = f"✅ 完成导入！成功 {len(success_files)} 个文件。"
        if failed_files:
            msg += f"\n❌ 失败 {len(failed_files)} 个文件：\n"
            for f, error in failed_files:
                msg += f"- {f} 错误: {error}\n"

        return msg
        
    def import_excel_to_mysql(self, file_path):
        try:
            print(file_path,'')
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
