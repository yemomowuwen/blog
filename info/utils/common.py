

def do_index_class(index):
    """自定义过滤器,过滤点击排序html的class"""

    if index == 1:
        return '/'
    elif index == 2:
        return 'about'
    elif index == 3:
        return 'share'
    elif index == 4:
        return 'list'
    elif index == 5:
        return 'info'
    else:
        return 'gbook'