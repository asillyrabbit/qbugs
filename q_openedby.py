from configure import Common
import sys


def q_openedby(month):
    month = f'{month[0:4]}-{month[4:]}'
    sql = f'select openedby,severity,count(*) from zt_bug where deleted="0" \
            and resolution in("fixed","postponed","") and openedDate \
            like "%{month}%" group by openedby,severity'

    conn = Common().conn
    cur = conn.cursor()
    cur.execute(sql)
    data_infos = cur.fetchall()
    cur.close()
    conn.close()

    name_value = {}
    name_desc = {}
    for name, level, count in data_infos:
        """
        count -- 提示*1，一般*3，严重*9
        """
        name_value.setdefault(name, 0)
        name_desc.setdefault(name, '')
        if level == 1 or level == 2:
            value = count * 9
            desc = f'严重{count}个，'
        elif level == 3:
            value = count * 3
            desc = f'一般{count}个，'
        elif level == 4:
            value = count
            desc = f'提示{count}个，'
        else:
            value = count
            desc = f'建议{count}个，'
        name_value[name] = name_value[name] + value
        name_desc[name] = name_desc[name] + desc

    if len(name_value) != 0:
        temp = sorted(name_value.items(), key=lambda kv: (kv[1], kv[0]))
        winner = temp[-1][0]
    else:
        winner = 'Kong'

    return winner, name_desc


if __name__ == "__main__":
    month = sys.argv[1]
    print(q_openedby(month))
