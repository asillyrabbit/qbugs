import pymysql
from flask import Flask
from flask import request

app = Flask(__name__)

# 数据库信息
dbinfo = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'passwd': '1234',
    'db': 'closer_db',
    'charset': 'utf8'
}


def conn_db(**dbinfo):
    """
    连接数据库
    """
    conn = pymysql.connect(**dbinfo)
    return conn


@app.route('/qmodule', methods=['POST'])
def qmodule():
    data_dict = request.form.to_dict()
    m_name = data_dict['m_name']

    fm_dict = query_fm(m_name)

    return fm_dict


@app.route('/qbugs_api', methods=['POST'])
def qbugs():
    data_dict = request.form.to_dict()
    m_name = data_dict['m_name']

    conn = conn_db(**dbinfo)
    cur = conn.cursor()

    am_dict = query_am(cur, m_name)
    am_bugs = query_bugs(cur, am_dict)

    cur.close()
    conn.close()

    return am_bugs


def query_fm(m_name):
    """
    fm：根（父）模块
    模糊匹配，返回根模块ID与名称
    """
    conn = conn_db(**dbinfo)
    cur = conn.cursor()

    fm_dict = {}
    q_fm = f"select id,name from zt_module where type='bug' and deleted='0' and name like'%{m_name}%' "
    cur.execute(q_fm)
    for (f_id, f_name) in cur.fetchall():
        fm_dict[f_id] = f_name

    cur.close()
    conn.close()

    return fm_dict


def query_am(cur, m_name):
    """
    am：所有模块
    返回跟模块及其所有子模块的ID和名称
    """
    am_dict = query_fm(m_name)
    am_ids = list(am_dict.keys())

    while len(am_ids) > 0:
        f_ids = str(am_ids).strip('[').strip(']')
        q_am = f"select id,name from zt_module where deleted='0' and parent in({f_ids})"
        cur.execute(q_am)
        am_ids.clear()
        for (m_id, m_name) in cur.fetchall():
            am_dict[m_id] = m_name
            am_ids.append(m_id)

    return am_dict


def query_bugs(cur, am_dict):
    am_bugs = {}
    for m_id, m_name in am_dict.items():
        # 公共查询条件
        q_comm = f"zt_bug where deleted='0' and resolution in('fixed','postponed','') and module='{m_id}'"
        # 全部
        q_total = f"select count(*) from {q_comm}"
        cur.execute(q_total)
        total = cur.fetchone()[0]
        # 重置公共查询条件
        q_comm = f"{q_comm} and status!='closed'"
        # 未关闭的
        q_opened = f"select count(*) from {q_comm}"
        cur.execute(q_opened)
        opened = cur.fetchone()[0]
        # 未关闭问题按分类
        type_dict = {}
        q_type = f"select type,count(*) from {q_comm} group by type"
        cur.execute(q_type)
        for b_type, count in cur.fetchall():
            b_type = tran_type(b_type)
            type_dict[b_type] = count
        # 未关闭问题按级别
        level_dict = {}
        q_level = f"select severity,count(*) from {q_comm} group by severity"
        cur.execute(q_level)
        for level, count in cur.fetchall():
            level = tran_level(level)
            level_dict[level] = count

        # 格式化数据
        m_bugs = {
            'total': total,
            'opened': opened,
            'type': type_dict,
            'level': level_dict
        }
        am_bugs[m_name] = m_bugs

    return am_bugs


def tran_level(level):
    if level == 1:
        level = '致命'
    if level == 2:
        level = '严重'
    if level == 3:
        level = '一般'
    if level == 4:
        level = '提示'
    if level == 5:
        level = '建议'

    return level


def tran_type(b_type):
    if b_type == 'function':
        b_type = '功能'
    if b_type == 'userexperience':
        b_type = '用户体验'
    if b_type == 'load':
        b_type = '性能'
    if b_type == 'compatibility':
        b_type = '兼容'
    if b_type == 'ui':
        b_type = 'UI'
    if b_type == 'demand':
        b_type = '需求'
    if b_type == 'security':
        b_type = '安全性'

    return b_type


if __name__ == '__main__':
    app.run(host='0.0.0.0')
