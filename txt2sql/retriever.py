import mysql.connector
from mysql.connector import Error

# use english prompt can promove the speed of response

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
        status = True
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
                return result,status

        except Error as e:
            print(f"❌ 获取表和字段信息失败：{e}")
            status = False
            return None,status


    def get_foreign_key_map(self):
        try:
            connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )

            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                query = """
                    SELECT 
                        TABLE_NAME AS table_name,
                        COLUMN_NAME AS column_name,
                        REFERENCED_TABLE_NAME AS referenced_table,
                        REFERENCED_COLUMN_NAME AS referenced_column
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL;
                """
                cursor.execute(query, (self.db_name,))
                foreign_keys = cursor.fetchall()

                foreign_key_map = {}
                for row in foreign_keys:
                    table = row['table_name']
                    column = row['column_name']
                    ref_table = row['referenced_table']
                    ref_column = row['referenced_column']
                    
                    if table not in foreign_key_map:
                        foreign_key_map[table] = {}
                    
                    foreign_key_map[table][column] = (ref_table, ref_column)
                
                cursor.close()
                connection.close()
                return foreign_key_map

        except Error as e:
            print(f"❌ 获取外键映射失败：{e}")
            return None
    
    