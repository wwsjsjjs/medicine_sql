"""
配置文件
包含资源限制、性能参数等配置
"""

import os


class Config:
    """基础配置"""
    # 应用密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///medicine.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 生产环境设为 False
    
    # 资源限制
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大请求体16MB
    
    # JSON配置
    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False
    
    # 分页配置
    ITEMS_PER_PAGE = 20
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = 3600  # 1小时


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # 显示SQL语句


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    
    # 生产环境数据库（可改为MySQL等）
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///medicine.db'
    
    # 日志配置
    LOG_LEVEL = 'INFO'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///medicine_test.db'
    WTF_CSRF_ENABLED = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


# 性能优化建议（针对大规模请求）
PERFORMANCE_RECOMMENDATIONS = """
生产环境部署建议：

1. 使用 Gunicorn 运行（多进程）：
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   
   参数说明：
   -w 4: 启动4个worker进程（建议：CPU核心数 * 2 + 1）
   -b: 绑定地址和端口
   --timeout 120: 请求超时时间
   --max-requests 1000: worker处理多少请求后自动重启
   --max-requests-jitter 50: 重启请求数的抖动范围

2. 使用 Nginx 反向代理：
   - 负载均衡
   - 静态文件服务
   - 请求限流
   - GZIP压缩

3. 数据库优化：
   - 使用 MySQL/PostgreSQL 替代 SQLite
   - 添加适当的索引
   - 使用连接池
   - 开启查询缓存

4. 缓存策略：
   - 使用 Redis 缓存热点数据
   - 使用 Flask-Caching 缓存视图
   - 前端使用 LocalStorage/SessionStorage

5. 限流保护：
   - 使用 Flask-Limiter 进行请求限流
   - 配置 Nginx 限流规则

6. 监控和日志：
   - 使用 Prometheus + Grafana 监控
   - 配置日志轮转
   - 错误追踪（如 Sentry）

示例 Gunicorn 配置文件（gunicorn_config.py）：
--------------------------------------------
import multiprocessing

bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

max_requests = 1000
max_requests_jitter = 50

accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 启动命令：
# gunicorn -c gunicorn_config.py app:app
"""
