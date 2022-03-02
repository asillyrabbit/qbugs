import sys
from configure import Common

# 接收参数：模块名
m_name = sys.argv[1]

if __name__ == "__main__":
    comm = Common()
    print(comm.query_fm(m_name))
