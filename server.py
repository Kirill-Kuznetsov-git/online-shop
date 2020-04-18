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
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


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


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    db_session.global_init('db/base.sqlite')
    if form.validate_on_submit():
        session = db_session.create_session()
        user = User(
            email=form.email.data,
            is_admin=False,
            cart=''
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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
            return render_template('catalog.html', products=x, goods=current_user.get_cart())
        else:
            return render_template('catalog.html', products=x)
    elif request.method == 'POST':
        session = db_session.create_session()
        try:
            for goods in session.query(Goods).filter(Goods.id == request.form['index']):
                if current_user.cart != '':
                    current_user.cart += ';' + str(goods.id)
                else:
                    current_user.cart = str(goods.id)
        except Exception:
            pass
        try:
            for goods in session.query(Goods).filter(Goods.id == request.form['index_del']):
                current_user.cart = current_user.get_cart()
                del current_user.cart[current_user.cart.index(goods.id)]
            current_user.cart = [str(i) for i in current_user.cart]
            current_user.cart = ';'.join(current_user.cart)
        except Exception:
            pass
        session.merge(current_user)
        session.commit()
        if category == 0:
            x = session.query(Goods).all()
        else:
            x = session.query(Goods).filter(Goods.category == f'Категория №{category}')
        return render_template('catalog.html', products=x, goods=current_user.get_cart())


@app.route('/profile/<red>', methods=['GET', 'POST'])
@app.route('/profile', methods=['GET', 'POST'])
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
        if i.goods.split(';') != ['']:
            for j in i.goods.split(';'):
                for k in session.query(Goods).filter(Goods.id == int(j)):
                    t.append(k)
                    price_all += k.price
            orders.append([r, t, price_all])
            r += 1
    return render_template('profile.html', form=form, red=red, cur_user=current_user, orders=orders, admin=current_user.is_admin)


@app.route('/cart/<int:category>', methods=['GET', 'POST'])
@app.route('/cart', methods=['GET', 'POST'])
def cart(category=0):
    if request.method == 'GET':
        if category == 0:
            x = session.query(Goods).filter(Goods.id.in_(current_user.get_cart()))
        else:
            x = session.query(Goods).filter(Goods.id.in_(current_user.get_cart()), Goods.category == f'Категория №{category}')
        t = 0
        for _ in x:
            t += 1
        flag = True if t == 0 else False
        return render_template('cart.html', goods=x, flag=flag)
    elif request.method == 'POST':
        try:
            for goods in session.query(Goods).filter(Goods.id == request.form['index_del']):
                current_user.cart = current_user.get_cart()
                del current_user.cart[current_user.cart.index(goods.id)]
            current_user.cart = [str(i) for i in current_user.cart]
            current_user.cart = ';'.join(current_user.cart)
        except Exception:
            pass
        try:
            x = request.form['orders']
            r = 0
            for i in session.query(Goods).filter(Goods.id.in_(current_user.get_cart())):
                r += i.price
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
            x = session.query(Goods).filter(Goods.id.in_(current_user.get_cart()))
        else:
            x = session.query(Goods).filter(Goods.id.in_(current_user.get_cart()), Goods.category == f'Категория №{category}')
        t = 0
        for _ in x:
            t += 1
        flag = True if t == 0 else False
        return render_template('cart.html', goods=x, flag=flag)


@app.route('/profile_goods/<int:id>', methods=['GET', 'POST'])
def profile_goods(id):
    if request.method == 'GET':
        session = db_session.create_session()
        x = session.query(Goods).filter(Goods.id == id)
        if current_user.is_authenticated:
            for i in x:
                if i.id in current_user.get_cart():
                    return render_template('goods_profile.html', goods=i, flag=True)
                return render_template('goods_profile.html', goods=i, flag=False)
    elif request.method == 'POST':
        session = db_session.create_session()
        try:
            for goods in session.query(Goods).filter(Goods.id == request.form['index']):
                if current_user.cart != '':
                    current_user.cart += ';' + str(goods.id)
                else:
                    current_user.cart = str(goods.id)
        except Exception:
            pass
        try:
            for goods in session.query(Goods).filter(Goods.id == request.form['index_del']):
                current_user.cart = current_user.get_cart()
                del current_user.cart[current_user.cart.index(goods.id)]
            current_user.cart = [str(i) for i in current_user.cart]
            current_user.cart = ';'.join(current_user.cart)
        except Exception:
            pass
        session.merge(current_user)
        session.commit()
        x = session.query(Goods).filter(Goods.id == id)
        for i in x:
            if i.id in current_user.get_cart():
                return render_template('goods_profile.html', goods=i, flag=True)
            return render_template('goods_profile.html', goods=i, flag=False)


@app.route('/add_goods', methods=['GET', 'POST'])
def add_goods():
    db_session.global_init('db/base.sqlite')
    session = db_session.create_session()
    form = AddForm()
    if form.validate_on_submit():
        goods = Goods(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            picture=form.picture.data,
            price=form.price.data
        )
        session.add(goods)
        session.commit()
        return render_template('add_goods.html', form=form)
    return render_template('add_goods.html', form=form)


if __name__ == '__main__':
    db_session.global_init('db/base.sqlite')
    session = db_session.create_session()
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, host='0.0.0.0')
