# Gunicorn 配置文件
# 用于生产环境部署

import multiprocessing
import os

# 服务器绑定地址
bind = "0.0.0.0:5000"

# Worker进程数量（建议：CPU核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# Worker类型（sync, eventlet, gevent, tornado）
worker_class = "sync"

# 每个worker的最大连接数
worker_connections = 1000

# 请求超时时间（秒）
timeout = 120

# Keep-Alive超时时间
keepalive = 5

# Worker处理多少请求后自动重启（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 进程名称
proc_name = "medicine_system"

# 守护进程模式（生产环境建议使用systemd或supervisor管理）
daemon = False

# 进程ID文件
pidfile = "gunicorn.pid"

# 用户和组（可选，提高安全性）
# user = "www-data"
# group = "www-data"

# 临时目录
tmp_upload_dir = None

# 打印配置信息
print(f"Gunicorn配置:")
print(f"  - Workers: {workers}")
print(f"  - Bind: {bind}")
print(f"  - Timeout: {timeout}s")
print(f"  - Max Requests: {max_requests}")
