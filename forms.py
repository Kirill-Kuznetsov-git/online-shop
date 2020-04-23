from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from models.users import User
from models import db_session


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(min=3, max=40), Email(message=None)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=40), EqualTo('password_again', message='Пароли не совпадают.')])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(), Length(min=6, max=40)])
    submit = SubmitField('Зарегистрироваться')

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        session = db_session.create_session()
        user = session.query(User).filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Пользователь уже зарегистрирован")
            return False
        if self.password.data.lower() == self.password.data:
            self.password.errors.append('В пароле должны содерожаться заглавные буквы')
            return False
        flag = False
        for i in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            if i in self.password.data:
                flag = True
                break
        if flag is False:
            self.password.errors.append('В пароле должны содерожаться цифры')
            return False
        return True


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        session = db_session.create_session()
        user = session.query(User).filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append("Пользователь не зарегистрирован")
            return False
        return True


class ProfileForm(FlaskForm):
    name = StringField('Имя', validators=[])
    surname = StringField('Фамилия', validators=[])
    country = StringField('Страна', validators=[])
    town = StringField('Город', validators=[])
    exit_btn = SubmitField('Выйти')
    edit_btn = SubmitField('Редактировать')
    save_btn = SubmitField('Сохранить')
    admin_btn = SubmitField('Создать продукт')


class AddForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    category = SelectField('Категория', validators=[DataRequired()], choices=[(1, 'Категория №1'),
                                                                              (2, 'Категория №2'),
                                                                              (3, 'Категория №3')], coerce=int)
    picture = StringField('Путь картинки', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    add_btn = SubmitField('Добавить')
