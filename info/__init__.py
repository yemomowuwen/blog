import redis
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_session import Session
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
redis_store = None  # type: StrictRedis

def setup_log(config_name):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

def create_app(config_name):
    app = Flask(__name__)
    setup_log(config_name)
    # config配置
    cur_config = config[config_name]
    # 配置
    app.config.from_object(cur_config)
    # 初始化数据库
    db.init_app(app)
    # 初始话redis
    global redis_store
    redis_store = redis.StrictRedis(host=cur_config.REDIS_HOST, port=cur_config.REDIS_PORT)
    # 开启csrf保护
    CSRFProtect(app)
    # 设置session保存位置
    Session(app)

    @app.after_request
    def after_request(response):
        # 调用函数生成csrf_token
        csrf_token = generate_csrf()
        # 通过cookie将值传给前端
        response.set_cookie('csrf_token', csrf_token)
        return response

    from info.module.index import index_blu
    app.register_blueprint(index_blu)
    from info.module.passport import passport_blu
    app.register_blueprint(passport_blu)
    from info.utils.common import do_index_class
    # 添加自定义过滤器
    app.add_template_filter(do_index_class, 'index_class')
    return app





