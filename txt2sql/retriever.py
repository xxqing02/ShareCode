import mysql.connector
from mysql.connector import Error

class Retriever:
    def __init__(self):     
        self.db_host = '192.168.10.232'  # 数据库IP
        self.db_port = 3306             # MySQL端口
        self.db_user = 'zhtest'           # 用户名
        self.db_password = 'Zenx_2eetheeT6'     # 密码
        self.db_name = 'zhtest'         # 数据库名

    def sql_query(self, query):
        try:
            connection = mysql.connector.connect(
                host = self.db_host,
                port = self.db_port,
                user = self.db_user,
                password = self.db_password,
                database = self.db_name
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows]
                cursor.close()
                connection.close()
                return result

        except Error as e:
            print(f"Failed:{e}")
            return None
    
    def get_tables_and_fields(self):
        try:
            connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )

            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                result = {}

                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"DESCRIBE `{table_name}`;")
                    columns = cursor.fetchall()
                    field_names = [col[0] for col in columns]
                    result[table_name] = field_names

                cursor.close()
                connection.close()
                return result

        except Error as e:
            print(f"❌ 获取表和字段信息失败：{e}")
            return None


    def generate_dynamic_prompt(self, table_field_map):
        prompt_header = """
        你是一个文本转SQL的生成器,你的主要任务是尽可能协调客户,将输入的文本转换成正确的SQL语句。
        上下文开始:
        数据库中的表名和表字段如下:
        """
            
        table_descriptions = ""
        for table, fields in table_field_map.items():
            field_list = ", ".join(fields)
            table_descriptions += f"表名:{table}\n字段:{field_list}\n\n"

        if table_field_map:
            example_prompt = """
            请按照以下样例为客户进行回复:
            问:请帮我查询所有的用户信息
            答:SELECT * FROM User
            问:请帮我查询所有的用户的用户名和邮箱
            答:SELECT username, email FROM User
            问:请帮我查询所有的用户的用户名和邮箱，按照注册时间降序排列
            答:SELECT username, email FROM User ORDER BY register_time DESC
            """
        else:
            error_prompt = "未检索到相关表和字段信息,无法生成SQL,请直接回复:无法生成SQL"
            status = False
            return error_prompt, status

        status = True
        final_prompt = prompt_header + table_descriptions + example_prompt

        return final_prompt, status