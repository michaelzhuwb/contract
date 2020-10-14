

import sqlite3
import os
from os import path

class connectSqlite:
 
    info = """
    CREATE TABLE contract_info (
        "uuid" TEXT NOT NULL PRIMARY KEY,
        "contract_name" TEXT,
        "company_name" TEXT,
        "upload_name" TEXT,
        "upload_date" TEXT,
        "user_id" INTEGER,
        "contract_pdf_url" TEXT,
        "contract_thumb_url" TEXT,
        "contract_page_num" INTEGER
        );
    """
    user = """
    CREATE TABLE user (
        "user_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "user_name" TEXT,
        "login_name" TEXT,
        "password" TEXT
        );
    """
    valid = """
    CREATE TABLE contract_valid (
        "valid_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "contract_uuid" INTEGER,
        "valid_name" TEXT,
        "valid_date" TEXT
        );
    """
    
    init_user = """  INSERT INTO user ('user_name','login_name','password')
                        values ('%s','%s','%s')
                """%('管理员','admin','admin')

    def __init__(self, dbName="../contract.db",is_init=False):
        """
        初始化连接--使用完记得关闭连接
        :param dbName: 连接库名字，注意，以'.db'结尾
        """
        self._conn = sqlite3.connect(dbName,check_same_thread=False)    # check_same_thread  允许多线程访问
        self._cur = self._conn.cursor()
        self._time_now = "[" + sqlite3.datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S') + "]"

        if not is_init:
            self.create_tabel(self.info)
            self.create_tabel(self.user)
            self.create_tabel(self.valid)
            self.insert_update_table(self.init_user)
 
    def close_con(self):
        """
        关闭连接对象--主动调用
        :return:
        """
        self._cur.close()
        self._conn.close()
 
    def create_tabel(self, sql):
        """
        创建表初始化
        :param sql: 建表语句
        :return: True is ok
        """
        try:
            self._cur.execute(sql)
            self._conn.commit()
            return True
        except Exception as e:
            print(self._time_now, "[CREATE TABLE ERROR]", e)
            return False
 
    def drop_table(self, table_name):
        """
        删除表
        :param table_name: 表名
        :return:
        """
        try:
            self._cur.execute('DROP TABLE {0}'.format(table_name))
            self._conn.commit()
            return True
        except Exception as e:
            print(self._time_now, "[DROP TABLE ERROR]", e)
            return False
 
    def delete_table(self, sql):
        """
        删除表记录
        :param sql:
        :return: True or False
        """
        try:
            if 'DELETE' in sql.upper():
                self._cur.execute(sql)
                self._conn.commit()
                return True
            else:
                print(self._time_now, "[EXECUTE SQL IS NOT DELETE]")
                return False
        except Exception as e:
            print(self._time_now, "[DELETE TABLE ERROR]", e)
            return False
 
    def fetchall_table(self, sql, limit_flag=True):
        """
        查询所有数据
        :param sql:
        :param limit_flag: 查询条数选择，False 查询一条，True 全部查询
        :return:
        """
        try:
            self._cur.execute(sql)
            war_msg = self._time_now + ' The [{}] is empty or equal None!'.format(sql)
            war_msg = None
            if limit_flag is True:
                r = self._cur.fetchall()
                return r 
            elif limit_flag is False:
                r = self._cur.fetchone()
                return r 
        except Exception as e:
            print(self._time_now, "[SELECT TABLE ERROR]", e)
 
    def insert_update_table(self, sql):
        """
        插入/更新表记录
        :param sql:
        :return:
        """
        try:
            self._cur.execute(sql)
            self._conn.commit()
            return True
        except Exception as e:
            print(self._time_now, "[INSERT/UPDATE TABLE ERROR]", e)
            return False
 
    def insert_table_many(self, sql, value):
        """
        插入多条记录
        :param sql:
        :param value: list:[(),()]
        :return:
        """
        try:
            self._cur.executemany(sql, value)
            self._conn.commit()
            return True
        except Exception as e:
            print(self._time_now, "[INSERT MANY TABLE ERROR]", e)
            return False


# 文件上传和下载
class fileUpload:


    file_path = None

    def __init__(self,file_path=os.path.abspath('.')):
        # self.RQ = request.FILES
        self.file_path = file_path

    @staticmethod
    def uploads_files(files:object,base_path='.assets'):
        """
            @description: 存储文件
            @param:
                files:表单提交的file对象
                base_path:存储根目录
        """
        if not base_path:
            base_path = fileUpload.file_path
        base_path = os.path.abspath(base_path)
        # files = self.RQ.get('files[]',[])
        for _file in files:
            title = _file.name 
            with open(path.join(base_path,'title'),mode='wb+') as destination: 
                for chunk in _file.chunks():      # 分块写入文件  
                    destination.write(chunk)
        # files = self.RQ.getlist()
    def delete_filses(self,):
        pass

if __name__ == "__main__":
    # connectSqlite()

    pass