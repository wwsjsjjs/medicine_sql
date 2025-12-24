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
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost:3306/medicine?charset=utf8mb4'
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

