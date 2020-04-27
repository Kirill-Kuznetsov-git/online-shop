from flask import Flask, render_template, redirect, request
from models import db_session
import flask_login
import os
from flask_login import login_user, logout_user, login_required, current_user
from models.users import User
from models.goods import Goods
from models.orders import Order
from forms import RegisterForm, LoginForm, ProfileForm, AddForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = os.getcwd() + '\static\img'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)

#авторизация
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    db_session.global_init('db/base.sqlite')
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/0")
        return render_template('login.html', title='Авторизация',
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

#регистрация
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    db_session.global_init('db/base.sqlite')
    if form.validate_on_submit():
        session = db_session.create_session()
        user = User(
            email=form.email.data,
            is_admin=False,
            cart='',
            goods_number=0
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

#основная страница
@app.route('/<int:category>', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def catalog(category=0):
    if request.method == 'GET':
        db_session.global_init('db/base.sqlite')
        session = db_session.create_session()
        if category == 0:
            x = session.query(Goods).all()
        else:
            x = session.query(Goods).filter(Goods.category == f'Категория №{category}')
        if current_user.is_authenticated:
            return render_template('catalog.html', products=x, goods=current_user.get_cart()[0])
        else:
            return render_template('catalog.html', products=x)
    elif request.method == 'POST':
        session = db_session.create_session()
        try:
            for goods in session.query(Goods).filter(Goods.id == request.form['index']):
                if current_user.cart != '':
                    current_user.cart += ';' + str(goods.id) + ';' + str(request.form['is_number'])
                else:
                    current_user.cart = str(goods.id) + ';' + str(request.form['is_number'])
                current_user.goods_number += 1
        except Exception:
            pass
        try:
            for goods in session.query(Goods).filter(Goods.id == request.form['index_del']):
                current_user.cart = current_user.get_cart()
                del current_user.cart[1][current_user.cart[0].index(goods.id)]
                del current_user.cart[0][current_user.cart[0].index(goods.id)]
            current_user.cart = [str(current_user.cart[0][i]) + ';' + str(current_user.cart[1][i]) for i in range(len(current_user.cart[0]))]
            current_user.cart = ';'.join(current_user.cart)
            current_user.goods_number -= 1
        except Exception:
            pass
        session.merge(current_user)
        session.commit()
        if category == 0:
            x = session.query(Goods).all()
        else:
            x = session.query(Goods).filter(Goods.category == f'Категория №{category}')
        return render_template('catalog.html', products=x, goods=current_user.get_cart()[0])

#профиль пользователя
@app.route('/profile/<red>', methods=['GET', 'POST'])
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile(red='edit'):
    form = ProfileForm()
    db_session.global_init('db/base.sqlite')
    session = db_session.create_session()
    try:
        a = request.form['edit_btn']
        return redirect('/profile/save')
    except Exception:
        pass
    try:
        a = request.form['save_btn']
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.town = form.town.data
        current_user.country = form.country.data
        session.merge(current_user)
        session.commit()
        return redirect('/profile/edit')
    except Exception:
        pass
    try:
        a = request.form['exit_btn']
        logout_user()
        return redirect('/')
    except Exception:
        pass
    try:
        r = request.form['admin_btn']
        return redirect('/add_goods')
    except Exception:
        pass
    orders = []
    r = 1
    for i in session.query(Order).filter(Order.user_id == current_user.id):
        t = []
        price_all = 0
        if i.get_goods != [[], []]:
            for j in range(len(i.get_goods()[0])):
                qwe = []
                qwe.append(session.query(Goods).filter(Goods.id == int(i.get_goods()[0][j])).first())
                qwe.append(i.get_goods()[1][j])
                qwe.append(str(int(session.query(Goods).filter(Goods.id == int(i.get_goods()[0][j])).first().price) * int(i.get_goods()[1][j])))
                t.append(qwe)
                price_all += int(session.query(Goods).filter(Goods.id == int(i.get_goods()[0][j])).first().price) * int(i.get_goods()[1][j])
            orders.append([r, t, price_all])
            r += 1
    print(orders)
    return render_template('profile.html', form=form, red=red, cur_user=current_user, orders=orders, admin=current_user.is_admin)

#корзина
@app.route('/cart/<int:category>', methods=['GET', 'POST'])
@app.route('/cart', methods=['GET', 'POST'])
def cart(category=0):
    if request.method == 'GET':
        if current_user.is_authenticated:
            if category == 0:
                x = session.query(Goods).filter(Goods.id.in_(current_user.get_cart()[0]))
            else:
                x = session.query(Goods).filter(Goods.id.in_(current_user.get_cart()[0]), Goods.category == f'Категория №{category}')
            t = 0
            for _ in x:
                t += 1
            flag = True if t == 0 else False
            return render_template('cart.html', goods=x, flag=flag, cur_cart=current_user.get_cart())
        else:
            return render_template('cart.html')
    elif request.method == 'POST':
        try:
            for goods in session.query(Goods).filter(Goods.id == request.form['index_del']):
                current_user.cart = current_user.get_cart()
                del current_user.cart[1][current_user.cart[0].index(goods.id)]
                del current_user.cart[0][current_user.cart[0].index(goods.id)]
            current_user.cart = [str(current_user.cart[0][i]) + ';' + str(current_user.cart[1][i]) for i in range(len(current_user.cart[0]))]
            current_user.cart = ';'.join(current_user.cart)
            current_user.goods_number -= 1
        except Exception:
            pass
        try:
            x = request.form['orders']
            current_user.goods_number = 0
            r = 0
            for i in range(len(current_user.get_cart()[0])):
                for _ in session.query(Goods).filter(Goods.id == current_user.get_cart()[0][i]):
                    g = session.query(Goods).filter(Goods.id == current_user.get_cart()[0][i]).first()
                    g.number -= current_user.get_cart()[1][i]
                    r += current_user.get_cart()[1][i] * g.price

            order = Order(
                goods=current_user.cart,
                user_id=current_user.id,
                price=r
            )

            current_user.cart = ''
            session.add(order)
            session.commit()
        except Exception:
            pass
        try:
            x = request.form['back_catalog']
            return redirect('/')
        except Exception:
            pass
        session.merge(current_user)
        session.commit()
        if category == 0:
            x = session.query(Goods).filter(Goods.id.in_(current_user.get_cart()[0]))
        else:
            x = session.query(Goods).filter(Goods.id.in_(current_user.get_cart()[0]), Goods.category == f'Категория №{category}')
        t = 0
        for _ in x:
            t += 1
        flag = True if t == 0 else False
        return render_template('cart.html', goods=x, flag=flag)

#профиль продуктов
@app.route('/profile_goods/<int:id>', methods=['GET', 'POST'])
def profile_goods(id):
    if request.method == 'GET':
        session = db_session.create_session()
        x = session.query(Goods).filter(Goods.id == id)
        for i in x:
            if current_user.is_authenticated:
                if i.id in current_user.get_cart()[0]:
                    return render_template('goods_profile.html', goods=i, flag=True)
                return render_template('goods_profile.html', goods=i, flag=False)
            else:
                return render_template('goods_profile.html', goods=i, flag=False)
    elif request.method == 'POST':
        session = db_session.create_session()
        try:
            for goods in session.query(Goods).filter(Goods.id == request.form['index']):
                if current_user.cart != '':
                    current_user.cart += ';' + str(goods.id) + ';' + str(request.form['is_number'])
                else:
                    current_user.cart = str(goods.id) + ';' + str(request.form['is_number'])
                current_user.goods_number += 1
        except Exception:
            pass
        try:
            for goods in session.query(Goods).filter(Goods.id == request.form['index_del']):
                current_user.cart = current_user.get_cart()
                del current_user.cart[1][current_user.cart[0].index(goods.id)]
                del current_user.cart[0][current_user.cart[0].index(goods.id)]
            current_user.cart = [str(current_user.cart[0][i]) + ';' + str(current_user.cart[1][i]) for i in range(len(current_user.cart[0]))]
            current_user.cart = ';'.join(current_user.cart)
            current_user.goods_number -= 1
        except Exception:
            pass
        session.merge(current_user)
        session.commit()
        x = session.query(Goods).filter(Goods.id == id)
        for i in x:
            if i.id in current_user.get_cart()[0]:
                return render_template('goods_profile.html', goods=i, flag=True)
            return render_template('goods_profile.html', goods=i, flag=False)

#добавление продукта для админа
@app.route('/add_goods', methods=['GET', 'POST'])
@login_required
def add_goods():
    if request.method == 'GET':
        db_session.global_init('db/base.sqlite')
        session = db_session.create_session()
        if not current_user.is_admin:
            return redirect('/')
        form = AddForm()
        return render_template('add_goods.html', form=form)
    elif request.method == 'POST':
        form = AddForm()
        session = db_session.create_session()
        k = 'Категория №' + str(form.category.data)
        q = 1
        for _ in session.query(Goods).all():
            q += 1
        file = request.files['file']
        file.save(app.config['UPLOAD_FOLDER'] + f"\{str(q)}.png")
        goods = Goods(
            name=form.name.data,
            description=form.description.data,
            category=k,
            picture=f"\static\img\{str(q)}.png",
            price=form.price.data,
            number=form.number.data
        )
        session.add(goods)
        session.commit()
        return render_template('add_goods.html', form=form)


if __name__ == '__main__':
    db_session.global_init('db/base.sqlite')
    session = db_session.create_session()
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, host='0.0.0.0')
