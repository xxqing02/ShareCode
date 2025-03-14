import mysql.connector
from mysql.connector import Error
import json

def execute_query_direct(query):
    try:
        # 数据库连接配置
        db_host = '192.168.10.232'  # 数据库IP
        db_port = 3306             # MySQL端口
        db_user = 'zhtest'           # 用户名
        db_password = 'Zenx_2eetheeT6'     # 密码
        db_name = 'zhtest'         # 数据库名

        # 连接MySQL
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )

        if connection.is_connected():
            print("✅ 数据库连接成功！")

            cursor = connection.cursor()
            cursor.execute(query)

            # 获取列名
            columns = [col[0] for col in cursor.description]

            # 获取结果
            rows = cursor.fetchall()

            # 结构化为 list[dict]
            result = [dict(zip(columns, row)) for row in rows]

            # 关闭
            cursor.close()
            connection.close()

            return result

    except Error as e:
        print(f"❌ 数据库连接或查询失败：{e}")
        return None


