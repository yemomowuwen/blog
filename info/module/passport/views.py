import re
import logging
import smtplib
from . import passport_blu
from email.mime.text import MIMEText
from email.header import Header
from flask import request, session
from flask import current_app, jsonify
from flask import make_response
from info import redis_store, db
from info.utils.captcha.captcha import captcha
from info.utils import recode, constants
from info.model.user import BlogCustomer
from datetime import datetime
from random import choice

logger = logging.getLogger(__name__)


def sms_email(receiver, code):
    # 使用网易发送邮箱验证码
    sender = '1242861695@qq.com'
    password = 'ykokjfhaadisigdg'

    message = MIMEText(f'您的Blog验证码是B-{code},五分钟内有效!!!')
    message['From'] = Header('Ye_Bolg', 'utf-8')
    message['To'] = Header(receiver, 'utf-8')

    subject = 'Blog注册'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)  # SMTP协议 默认端口25
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())
        server.quit()
    except smtplib.SMTPException:
        return -1


@passport_blu.route('/image_code')
def get_image_code():
    """获取图片验证吗"""
    code_id = request.args.get('imageCodeId')
    # 生成验证吗
    name, text, image = captcha.generate_captcha()
    try:
        # 保存当前生成的图片验证码内容
        redis_store.setex(f'ImageCode_{code_id}', constants.Image_Timeout, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=recode.DATAERR, errmsg='保存数据失败!'))

    # 返回响应内容
    resp = make_response(image)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


@passport_blu.route('/sms_code', methods=['POST'])
def send_email_code():
    """发送邮箱验证码"""
    param_dict = request.json
    email = param_dict.get('email')
    image_code = param_dict.get('image_code')
    image_code_id = param_dict.get('image_code_id')

    if not all([email, image_code, image_code_id]):
        return jsonify(errno=recode.PARAMERR, errmsg='参数不足')

    if not re.match('^[a-z0-9A-Z]+[- | a-z0-9A-Z . _]+@([a-z0-9A-Z]+(-[a-z0-9A-Z]+)?\\.)+[a-z]{2,}$', email):
        # 邮箱错误
        return jsonify(errno=recode.DATAERR, errmsg='手机号不正确')

    # 去redis查询图片验证吗内容
    try:
        real_image_code = redis_store.get(f'ImageCode_{image_code_id}')
        if real_image_code:
            real_image_code = real_image_code.decode()
            redis_store.delete(f'ImageCode_{image_code_id}')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=recode.DBERR, errmsg='获取图片验证吗失败')

    if not real_image_code:
        return jsonify(errno=recode.NODATA, errmsg='验证码已过期')

    if image_code.lower() != real_image_code.lower():
        return jsonify(errno=recode.NODATA, errmsg='验证码输入错误')

    # 校验该邮箱是否已经注册过
    try:
        user = BlogCustomer.query.filter_by(email=email).first()
    except Exception as e:
        return jsonify(errno=recode.DBERR, errmsg='数据库查询错误')
    if user:
        return jsonify(errno=recode.DATAEXTST, errmsg='该邮箱已被注册')

    # 生成发送邮箱验证吗
    result = ''.join(choice('0123456789') for _ in range(6))
    a = sms_email(email, result)
    if a == -1:
        return jsonify(errno=recode.DATAERR, errmsg='发送邮箱验证码失败')
    # 保存验证码内容
    try:
        redis_store.setex(f'SMS_{email}', constants.Verify_Code_Timeout, result)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=recode.DBERR, errmsg='保存短信验证吗失败')
    return jsonify(errno=recode.OK, errmsg='发送成功')


@passport_blu.route('/register', methods=['POST'])
def register():
    """邮箱注册"""
    json_data = request.json
    email = json_data.get('email')
    sms_code = json_data.get('smscode')
    password = json_data.get('password')

    if not all([email, sms_code, password]):
        return jsonify(errno=recode.PARAMERR, errmsg='参数不全')

    # 从redis中获取指定邮箱对应的验证码
    try:
        real_sms_code = redis_store.get(f'SMS_{email}')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=recode.DBERR, errmsg='获取验证码失败')

    if not real_sms_code:
        return jsonify(errno=recode.NODATA, errmsg='短信验证码过期')

    # 校验验证码
    if sms_code != real_sms_code.decode():
        return jsonify(errno=recode.DATAERR, errmsg='短信验证码错误')

    # 删除验证码
    try:
        redis_store.delete(f'SMS_{email}')
    except Exception as e:
        current_app.logger.error(e)

    # 初始化user模型
    blog_customer = BlogCustomer()
    blog_customer.email = email
    blog_customer.password = password
    blog_customer.nick_name = email

    try:
        db.session.add(blog_customer)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)

        # 数据保存错误
        return jsonify(errno=recode.DATAERR, errmsg='数据保存失败')
    # 保存用户的登录状态
    session['customer_id'] = blog_customer.id
    session['nick_name'] = blog_customer.nick_name
    session['email'] = blog_customer.email

    # 返回注册结果
    return jsonify(errno=recode.OK, errmsg='OK')

@passport_blu.route('/login', methods=['POST'])
def login():
    json_data = request.json

    email = json_data.get('email')
    password = json_data.get('password')

    if not all([email, password]):
        return jsonify(errno=recode.PARAMERR, errmsg='参数不全')

    # 从数据库查询出指定用户
    try:
        blog_customer = BlogCustomer.query.filter_by(email=email).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=recode.DBERR, errmsg='查询数据错误')

    if not blog_customer:
        return jsonify(errno=recode.USERERR, errmsg='用户不存在')

    # 校验密码
    if not blog_customer.check_password(password):
        return jsonify(errno=recode.PWDERR, errmsg='密码错误')

    # 保存登录状态
    session['customer_id'] = blog_customer.id
    session['nick_name'] = blog_customer.nick_name
    session['email'] = blog_customer.email

    # 记录用户最后一次登录时间
    blog_customer.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=recode.OK, errmsg='OK')


@passport_blu.route('/login_out', methods=['POST'])
def logout():
    """登出功能"""
    session.pop('customer_id', None)
    session.pop('nick_name', None)
    session.pop('email', None)

    return jsonify(errno=recode.OK, errmsg='OK')






































