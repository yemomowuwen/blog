from . import index_blu
from flask import render_template, redirect, session, current_app
from flask import url_for, request, jsonify, current_app, g
from info.model.user import BlogCustomer, Articles, BlogAuthor, Category
from info.utils import constants, recode
from common import user_login_data



@index_blu.route('/index')
@user_login_data
def index():
    blog_customer = g.blog_customer
    customer_info = None
    if blog_customer:
        customer_info = {
            'customer_id': blog_customer.id if blog_customer else None,
            'nick_name': blog_customer.nick_name if blog_customer else None,
            'avatar_url': blog_customer.avatar_url if blog_customer else None
        }
    # 获取博主个人信息
    author = None
    try:
        author = BlogAuthor.query.get(1)
    except Exception as e:
        current_app.logger.error(e)

    author = {
        'title': author.title,
        'keywords': author.keywords,
        'description': author.description,
        'wechat': author.wechat,
        'qq': author.qq,
        'email': author.email,
        'wechat_reword': author.Wechat_Reward,
        'logo': author.logo,
        'avator_url': author.avator_url,
        'name': author.name,
        'tag': author.tag,
        'about_me': author.about_me
    }
    data = public()
    data['customer_info'] = customer_info if customer_info else None
    return render_template('index.html', data=data)


@index_blu.route('/articles_list')
def get_articles_list():
    # 获取参数
    args_dict = request.args
    page = args_dict.get('p', '1')
    per_page = args_dict.get('per_page', constants.HOME_PAGE_MAX_NEWS)
    category_id = args_dict.get('cid', 1)

    # 校验参数
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=recode.PARAMERR, errmsg='参数错误')

    # 查询数据分页
    filters = []
    try:
        paginate = Articles.query.order_by(Articles.create_time.desc()).paginate(page, per_page, False)
        # 获取查询出来的数据
        items = paginate.items
        # 获取到总页数
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=recode.DBERR, errmsg='数据查询失败')

    articles_list = []
    for articles in items:
        article_dict = {
            'id': articles.id,
            'title': articles.title,
            'digest': articles.digest,
            'index_image_url': articles.index_image_url,
            'create_time': articles.create_time,
            'clicks': articles.clicks,
            'tag': articles.tag
        }

        articles_list.append(article_dict)
    return jsonify(errno=recode.OK, errmsg='OK', total_Page=total_page, current_Page=current_page, articles_List=articles_list)


@index_blu.route('/info/<int:new_id>')
@user_login_data
def news_detail(new_id):
    blog_customer = g.blog_customer
    customer_info = {
        'customer_id': blog_customer.id if blog_customer else None,
        'nick_name': blog_customer.nick_name if blog_customer else None,
        'avatar_url': blog_customer.avatar_url if blog_customer else None
    }
    # 查询出详情数据
    try:
        article = Articles.query.filter_by(id=new_id).scalar()
    except Exception as e:
        return jsonify(errno=recode.DBERR, errmsg='数据查询失败')
    # 根据user_id查询出作者
    try:
        blog_customer = BlogCustomer.query.filter_by(id=article.user_id).scalar()
    except Exception as e:
        return jsonify(errno=recode.DBERR, errmsg='数据查询失败')

    article_dict = {
        'id': article.id,
        'title': article.title,
        'user_name': blog_customer.nick_name if blog_customer else None,
        'email': blog_customer.email if blog_customer else None,
        'create_time': article.create_time,
        'clicks': article.clicks,
        'tag': article.tag,
        'digest': article.digest,
        'content': article.content
    }

    data = public()
    data['user_info'] = customer_info if customer_info else None
    data['article_dict'] = article_dict
    return render_template('info.html', data=data)


def public():
    # 获取博主个人信息
    author = None
    try:
        author = BlogAuthor.query.get(1)
    except Exception as e:
        current_app.logger.error(e)

    author = {
        'title': author.title,
        'keywords': author.keywords,
        'description': author.description,
        'wechat': author.wechat,
        'qq': author.qq,
        'email': author.email,
        'wechat_reword': author.Wechat_Reward,
        'logo': author.logo,
        'avator_url': author.avator_url,
        'name': author.name,
        'tag': author.tag,
        'about_me': author.about_me
    }

    # 获取排行数据
    articles_list = None
    try:
        articles_list = Articles.query.order_by(Articles.clicks.desc()).limit(constants.Click_Max_Articles)
    except Exception as e:
        current_app.logger.error(e)

    click_articles_list = []
    for articles in articles_list if articles_list else []:
        articles_dict = {
            'id': articles.id,
            'title': articles.title,
            'digest': articles.digest,
            'index_image_url': articles.index_image_url
        }
        click_articles_list.append(articles_dict)

    # 站长推荐
    r_articles_list = None
    try:
        r_articles_list = Articles.query.filter(Articles.recommend != None).order_by(Articles.recommend.desc()).limit(
            constants.Recommend_Max_Articles)
    except Exception as e:
        current_app.logger.error(e)

    recommend_articles_list = []
    for r_articles in r_articles_list if r_articles_list else []:
        r_articles_dict = {
            'id': r_articles.id,
            'title': r_articles.title,
            'digest': r_articles.digest,
            'index_image_url': r_articles.index_image_url
        }
        recommend_articles_list.append(r_articles_dict)

    # 获取新闻分类数据
    categories = Category.query.all()
    # 定义列表保存分类数据
    categories_dicts_list = []

    for category in categories:
        c_dict = {'id': category.id,
                  'name': category.name}
        categories_dicts_list.append(c_dict)

    data = {
        'click_articles_list': click_articles_list,
        'author': author,
        'recommend_articles_list': recommend_articles_list,
        'categories': categories_dicts_list
    }
    return data