from . import index_blu
from flask import render_template, redirect, session, current_app
from flask import url_for, request, jsonify, current_app
from info.model.user import BlogCustomer, Articles, BlogAuthor, Category
from info.utils import constants, recode



@index_blu.route('/index')
def index():
    # 获取当前用户的id
    customer_id = session.get('customer_id')
    # 通过id获取信息
    blog_customer = None
    customer_info = None
    if customer_id:
        try:
            blog_customer = BlogCustomer.query.get(customer_id)
        except Exception as e:
            current_app.logger.error(e)

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
        r_articles_list = Articles.query.filter(Articles.recommend != None).order_by(Articles.recommend.desc()).limit(constants.Recommend_Max_Articles)
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
        'customer_info': customer_info if customer_info else None,
        'click_articles_list': click_articles_list,
        'author': author,
        'recommend_articles_list': recommend_articles_list,
        'categories': categories_dicts_list
        }

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