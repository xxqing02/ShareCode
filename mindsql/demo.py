from mindsql.core import MindSQLCore
from mindsql.databases import Sqlite
from mindsql.llms import GoogleGenAi
from mindsql.vectorstores import ChromaDB

# 配置API密钥
config = {"api_key": "YOUR-API-KEY"}

# 创建MindSQLCore实例
minds = MindSQLCore(
    llm=GoogleGenAi(config=config),
    vectorstore=ChromaDB(),
    database=Sqlite()
)

# 连接数据库
connection = minds.database.create_connection(url="YOUR_DATABASE_CONNECTION_URL")

# 索引数据库结构
minds.index_all_ddls(connection=connection, db_name='NAME_OF_THE_DB')

# 执行查询
response = minds.ask_db(
    question="您的自然语言查询",
    connection=connection,
    visualize=True
)

# 显示结果
print(response["result"])
if "chart" in response:
    response["chart"].show()

# 关闭连接
connection.close()