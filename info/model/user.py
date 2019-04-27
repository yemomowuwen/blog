from .base import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from info import db

# 用户收藏表,表示多对多关系
tb_user_collection = db.Table('info_user_collection',
                            db.Column('user_id', db.Integer, db.ForeignKey('blog_customer.id'), primary_key=True),
                            db.Column('article_id', db.Integer, db.ForeignKey('info_articles.id'), primary_key=True),
                            db.Column('create_time', db.DateTime, default=datetime.now))


class BlogCustomer(BaseModel, db.Model):
    """博主个人信息"""
    __tablename__ = 'blog_customer'

    id = db.Column(db.Integer, primary_key=True)  # id
    name = db.Column(db.String(32), nullable=True)  # 姓名
    nick_name = db.Column(db.String(32),unique=True, nullable=False)  # 昵称
    avatar_url = db.Column(db.String(128))  # 头像
    password_hash = db.Column(db.String(128), nullable=False)  # 密码hash
    mobile = db.Column(db.String(11))  # 手机号
    job = db.Column(db.String(64))  # 职业
    gender = db.Column(db.Enum('MAN', 'WOMAN'), default='MAN')  # 性别
    last_login = db.Column(db.DateTime, default=datetime.now)  # 最后登录时间
    is_admin = db.Column(db.Boolean, default=False)  # 是否是管理员
    is_author = db.Column(db.Boolean, default=False)  # 是否是博主
    signature = db.Column(db.String(512))  # 用户签名
    email = db.Column(db.String(64), nullable=False)  # 邮箱,注册时可用
    website = db.Column(db.TEXT)  # 简介
    area = db.Column(db.String(128))  # 地址
    wechat = db.Column(db.String(32))  # 微信
    wechat_url = db.Column(db.String(128))  # 微信url
    qq = db.Column(db.String(32))  # QQ
    qq_url = db.Column(db.String(128))  # QQurl
    keep = db.Column(db.String(128))  # 保留字段
    keep_url = db.Column(db.String(128)) # 保留url
    collection_news = db.relationship('Article', secondary=tb_user_collection, lazy='dynamic')

    def make_password_hash(self, password):
        # 将未加密的密码执行加密操作
        self.password_hash = generate_password_hash(password)

    # 重写getter方法
    @property
    def password(self):
        raise AttributeError('当前属性不可读')

    # 重写setter方法
    @password.setter
    def password(self, password):
        # 将未加密的密码调用generate_password_hash进行hash加密处理
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # 将未加密的密码传入,使用check_password_hash进行对比,正确为true
        return check_password_hash(self.password_hash, password)

class Articles(BaseModel, db.Model):
    """文章"""
    __tablename__ = 'info_articles'

    id = db.Column(db.Integer, primary_key=True)  # 文章id
    title = db.Column(db.String(256), nullable=False)  # 文章标题
    source = db.Column(db.String(64))  # 文章来源
    digest = db.Column(db.String(512), nullable=False)  # 文章摘要
    content = db.Column(db.Text, nullable=False)  # 文章内容
    clicks = db.Column(db.Integer, default=0)  # 浏览量
    index_image_url = db.Column(db.String(256))  # 文章列表图片路径
    category_id = db.Column(db.Integer, db.ForeignKey('info_category.id'))  # 文章分类
    user_id = db.Column(db.Integer, db.ForeignKey('blog_customer.id'))  # 文章作者
    comments = db.relationship('Comment', lazy='dynamic')


class Comment(BaseModel, db.Model):
    """评论"""
    __tablename__ = 'info_comment'

    id = db.Column(db.Integer, primary_key=True)  # 评论编号
    user_id = db.Column(db.Integer, db.ForeignKey('blog_customer.id'), nullable=False)  # 用户id
    articles_id = db.Column(db.Integer, db.ForeignKey('info_articles.id'), nullable=False)  # 文章id
    content = db.Column(db.Text, nullable=False)  # 评论内容
    parent_id = db.Column(db.Integer, db.ForeignKey('info_comment.id'))  # 父评论
    parent = db.relationship('Comment', remote_side=[id])  # 自关联
    like_count = db.Column(db.Integer, default=0)  # 点赞次数

class CommentLike(BaseModel, db.Model):
    """评论点赞"""
    __tablename__ = 'info_comment_like'
    comment_id = db.Column('comment_id', db.Integer, db.ForeignKey('info_comment.id'), primary_key=True)  # 评论编号
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('blog_customer.id'), primary_key=True)  # 用户编号

class Category(BaseModel, db.Model):
    """文章分类"""
    __tablename__ = 'info_category'

    id = db.Column(db.Integer, primary_key=True)  # 分类编号
    name = db.Column(db.String(64), nullable=False)  # 分类名
    articles_list = db.relationship('Articles', backref='category', lazy='dynamic')

class Carousels(BaseModel, db.Model):
    """轮播图"""
    __tablename__ = 'info_carousels'

    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(64))  # 轮播图名字
    categ = db.Column(db.Integer, nullable=False)  # 种类







