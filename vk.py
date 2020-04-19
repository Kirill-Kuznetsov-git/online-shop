import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import requests
import random
import json
from models.users import User
from models.goods import Goods
from models.orders import Order
from models import db_session
import datetime


token = '89b6497b72c0b96cf2c6f4406d5052e4a8490bc99c4943032a5d1192afa83c5bf4e8b6fef49fdf37a2aa4'
group_id = '193939883'
album_id = '274267024'


def main():
    vk_session = vk_api.VkApi(
        token=token)

    longpoll = VkBotLongPoll(vk_session, group_id)

    t = ['привет', 'здравствуйте', 'hi', 'hello']
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            flag = False
            for i in t:
                if i in event.obj.message['text'].lower():
                    flag = True
                    break
            if flag:
                response = requests.get('https://api.vk.com/method/users.get',
                                        params={'user_ids': event.obj.message['from_id'],
                                                'access_token': token,
                                                'v': '5.103'}).json()
                name = response['response'][0]['first_name']
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f"Здравствуйте {name}!\nВы можете узнать есть ли товары в наличии, если введете 'Товар:[название товара]'.\n"
                                         f" Также вы можете узнать какие у вас активные заказы, если введете логин.",
                                 random_id=random.randint(0, 2 ** 64))
                flag = False
            elif 'Товар' in event.obj.message['text']:
                db_session.global_init('db/base.sqlite')
                session = db_session.create_session()
                for i in session.query(Goods).filter(Goods.name == event.obj.message['text'].split(':')[1]):
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message=f"Товар есть в наличии."
                                             f"{i.name}\n{i.category}\n{i.description}\nЦена: {i.price} руб.",
                                     random_id=random.randint(0, 2 ** 64))
            elif '@' in event.obj.message['text']:
                db_session.global_init('db/base.sqlite')
                session = db_session.create_session()
                flag = False
                for i in session.query(User).filter(User.email == event.obj.message['text']):
                    flag = True
                    t = int(i.id)
                    a = 1
                    for j in session.query(Order).filter(Order.user_id == t):
                        res = ''
                        price_all = 0
                        q = j.goods.split(';')
                        for o in q:
                            for k in session.query(Goods).filter(Goods.id == int(o)):
                                res += k.name + ': ' + str(k.price) + '\n'
                                price_all += int(k.price)

                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=f"Заказ №{a}\n{res}Итого: {str(price_all)}.",
                                         random_id=random.randint(0, 2 ** 64))
                        a += 1
                    if a == 1:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message=f"У вас нет активных заказов",
                                         random_id=random.randint(0, 2 ** 64))
                if flag is False:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message=f"Некоректно введеный логин",
                                     random_id=random.randint(0, 2 ** 64))
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f"Вы можете узнать есть ли товары в наличии, если введете 'Товар:[название товара]'.\n"
                                         f" Также вы можете узнать какие у вас активные заказы, если введете логин.",
                                 random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
