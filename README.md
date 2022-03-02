# qbugs
# 面临问题
- 禅道数据库无法直接访问（服务器端口未放开）

# 解决方案
- 通过远程访问服务器，执行SSH命令获取数据
```
query_commd = f'python3 {远程目录}/qbugs.py 传入参数'
stdin, stdout, stderr = conn.exec_command(query_commd)
names = stdout.read().decode()
return names
```
