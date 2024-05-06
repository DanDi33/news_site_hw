from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import Length, Regexp, Email, DataRequired, EqualTo, ValidationError
from connect_db import db
from models import User


class EditUsernameForm(FlaskForm):
    name = StringField("Логин", validators=[Length(min=4, max=25, message="Имя должно содержать от 4 до 25 символов"),
                                            Regexp("^[A-Za-z0-9@#$%^&+=]{3,26}$",
                                                   message="Для имени пользователя разрешены "
                                                           "только латинские буквы, цифры и спецсимволы(без пробелов)."),
                                            ])
    submit = SubmitField("Сохранить изменения")


class EditEmailForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    submit = SubmitField("Сохранить изменения")


class EditPasswordForm(FlaskForm):
    old_psw = PasswordField("Старый пароль: ", validators=[DataRequired(), Regexp("^[A-Za-z0-9@#$%^&+=]{3,26}$",
                                                                                  message="Для пароля разрешены "
                                                                                          "только  латинские буквы, "
                                                                                          "цифры и"
                                                                                          "спецсимволы(без пробелов)."),
                                                           Length(min=4, max=100,
                                                                  message="Пароль должен содержать от 4 до 100 "
                                                                          "символов")])
    new_psw = PasswordField("Новый пароль: ", validators=[DataRequired(), Regexp("^[A-Za-z0-9@#$%^&+=]{3,26}$",
                                                                                 message="Для пароля разрешены "
                                                                                         "только  латинские буквы, "
                                                                                         "цифры и"
                                                                                         "спецсимволы(без пробелов)."),
                                                          Length(min=4, max=100,
                                                                 message="Пароль должен содержать от 4 до 100 "
                                                                         "символов")])
    psw2 = PasswordField("Повторите пароль: ",
                         validators=[DataRequired(), EqualTo('new_psw', message="Пароли должны совпадать")])
    submit = SubmitField("Сохранить изменения")


class AddPostForm(FlaskForm):
    title = StringField("Заголовок",
                        validators=[Length(min=2, max=200, message="Имя должно содержать от 2 до 200 символов"), ],
                        description="Заголовок")
    description = StringField("Краткое описание новости",
                              validators=[
                                  Length(min=2, max=300, message="Имя должно содержать от 2 до 200 символов"), ],
                              description="Краткое описание новости")
    # category = SelectField("Logo 1",
    #                        choices=[(option.id, option.name) for option in db.Category.query.all()], default=None)


class EditCategoryForm(FlaskForm):
    name = StringField("Категория", validators=[Length(min=4, max=25, message="Название категории должно содержать от 4"
                                                                              "до 25 символов"), ],
                       description="Введите категорию")
    submit = SubmitField("Сохранить изменения")


class DeleteCategoryForm(FlaskForm):
    name = StringField("Вы уверены что хотите удалить категорию?", validators=[Length(min=4, max=25, message="Название категории должно содержать от 4"
                                                                              "до 25 символов"), ],
                       description="Введите категорию")
    submit = SubmitField("Да, удалить")
