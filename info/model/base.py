from datetime import datetime
from info import db


class BaseModel(object):
    """模型基类,为每个模型补充创建时间和更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间
