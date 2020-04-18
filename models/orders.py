import sqlalchemy
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase, UserMixin):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    goods = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)

    def get_goods(self):
        if self.goods.split(';')[0] == '':
            q = []
        else:
            q = self.goods.split(';')
        return [int(i) for i in q]
