import sqlalchemy
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase, UserMixin):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    goods = sqlalchemy.Column(sqlalchemy.String)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    price = sqlalchemy.Column(sqlalchemy.Integer)

    def get_goods(self):
        print(2)
        if self.goods.split(';')[0] == '':
            return [[], []]
        else:
            x = [[], []]
            for i in range(len(self.goods.split(';'))):
                if i % 2 == 0:
                    x[0].append(int(self.goods.split(';')[i]))
                else:
                    x[1].append(int(self.goods.split(';')[i]))
            return x
