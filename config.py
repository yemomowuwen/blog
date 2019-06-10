import redis
import logging


class Config(object):
    """工程配置信息"""
    SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA"
    DEBUG = True

    # 數據庫的配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/blog"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # session配置
    SESSION_TYPE = "redis"  # 指定session保存到redis中
    SESSION_USE_SIGNER = True  # 讓cookie中的session_id被加密簽名處理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用redis的實例
    PERMANENT_SESSION_LIFETIME = 86400  # session的有效器,單位是秒


class DevelopmentConfig(Config):
    """開發模式下的配置"""
    DEBUG = True

    # 默認日誌等級
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """生產模式下的配置"""
    pass

    # 生產日誌等級
    LOG_LEVEL = logging.ERROR


# 定義配置字點
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}