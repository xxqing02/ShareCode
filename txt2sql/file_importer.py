import pandas as pd
from sqlalchemy import create_engine
import logging

# 配置日志记录
logging.basicConfig(
    filename='import_log.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ExcelToMySQL:
    def __init__(self, db_config):
        """
        初始化数据库连接配置
        :param db_config: 数据库连接参数
        """
        self.db_config = db_config
        self.engine = create_engine(
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )

    def import_excel_to_mysql(self, file_path):
        """
        将 Excel 文件中的每个 sheet 导入到 MySQL 数据库中
        :param file_path: Excel 文件路径
        """
        try:
            # 加载 Excel 文件
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names
            logging.info(f"📂 开始处理文件：{file_path}")
            logging.info(f"📄 发现 {len(sheet_names)} 个 sheet：{sheet_names}")

            for sheet in sheet_names:
                try:
                    # 读取 sheet 数据
                    df = pd.read_excel(xls, sheet_name=sheet)

                    # 清洗数据
                    df.replace("", None, inplace=True)  # 替换空字符串为 None
                    df.replace("nan", None, inplace=True)  # 替换 "nan" 字符串为 None
                    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # 去除字符串两端空格

                    # 生成表名
                    table_name = sheet.strip().replace(" ", "_").replace("-", "_").lower()
                    logging.info(f"🛠️ 正在处理 sheet：{sheet} -> 表名：{table_name}")

                    # 写入 MySQL 数据库
                    df.to_sql(name=table_name, con=self.engine, index=False, if_exists='replace')
                    logging.info(f"✅ 成功导入 sheet：{sheet} 到表：{table_name}")

                except Exception as e:
                    logging.error(f"⚠️ Sheet {sheet} 导入失败：{e}")

            logging.info(f"✅ 文件 {file_path} 处理完成！")
            return f"成功导入 {len(sheet_names)} 个 sheet 到数据库。"

        except Exception as e:
            logging.error(f"❌ 文件 {file_path} 处理失败：{e}")
            return f"文件 {file_path} 处理失败：{e}"

# 数据库配置
db_config = {
    'host': '192.168.10.232',
    'port': 3306,
    'user': 'zhtest',
    'password': 'Zenx_2eetheeT6',
    'database': 'zhtest'
    }
