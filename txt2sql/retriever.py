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
        You are an SQL query generator that converts natural language requests into accurate SQL statements. Your primary goal is to assist users by generating correct and efficient SQL queries based on their requests.
        
        Context:
        The database contains the following tables and fields:
        """
            
        table_descriptions = ""
        for table, fields in table_field_map.items():
            field_list = ", ".join(fields)
            table_descriptions += f"Table Name: {table}\nFields: {field_list}\n\n"

        if table_field_map:
            example_prompt = """
            Please follow the examples below to respond to user requests:
            
            User: Retrieve all user information.
            Response: SELECT * FROM User;
            
            User: Retrieve all usernames and emails of users.
            Response: SELECT username, email FROM User;
            
            User: Retrieve all usernames and emails of users, sorted by registration time in descending order.
            Response: SELECT username, email FROM User ORDER BY register_time DESC;
            
            Guidelines:
            - Always use valid SQL syntax.
            - If a field or table is not explicitly mentioned, inferring the relevant option based on common database structures is strictly forbidden.
            - Ensure queries are optimized and avoid unnecessary clauses.
            """
        else:
            error_prompt = "No table or field information found. Unable to generate SQL. Please respond with: 'Unable to generate SQL due to missing table and field details.'"
            status = False
            return error_prompt, status

        status = True
        final_prompt = prompt_header + table_descriptions + example_prompt

        return final_prompt, status
    