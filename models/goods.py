import sqlalchemy
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class Goods(SqlAlchemyBase, UserMixin):
    __tablename__ = 'goods'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    category = sqlalchemy.Column(sqlalchemy.String)
    picture = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)

    def get_goods(self):
        if self.goods.split(';')[0] == '':
            q = []
        else:
            q = self.goods.split(';')
        return [int(i) for i in q]
