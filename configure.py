import pymysql


class Common:
    def __init__(self):
        self.dbinfo = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'passwd': '1234',
            'db': 'closer_db',
            'charset': 'utf8'
        }
        self.conn = pymysql.connect(**self.dbinfo)

    def query_fm(self, m_name):
        """
        fm：根（父）模块
        模糊匹配，返回根模块ID与名称
        """
        cur = self.conn.cursor()

        fm_dict = {}
        q_fm = f"select id,name from zt_module where type='bug' and deleted='0' and name like'%{m_name}%' "
        cur.execute(q_fm)
        for (f_id, f_name) in cur.fetchall():
            fm_dict[f_id] = f_name

        cur.close()
        self.conn.close()

        return fm_dict
