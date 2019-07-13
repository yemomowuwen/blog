import functools
from flask import session, g



def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # 獲取到當前登錄用戶的id
        customer_id = session.get("customer_id")
        # 通過id獲取用戶信息
        blog_customr = None
        if customer_id:
            from info.model.user import BlogCustomer
            try:
                blog_customr = BlogCustomer.query.get(customer_id)
            except Exception:
                blog_customr = None
        g.blog_customer = blog_customr
        return f(*args, **kwargs)
    return wrapper



