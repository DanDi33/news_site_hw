import os

import flask
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, send_from_directory, g
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import secure_filename

from adminpanel.useful.forms import (EditUsernameForm,
                                     EditEmailForm,
                                     EditPasswordForm,
                                     EditCategoryForm,
                                     DeleteCategoryForm,
                                     AddPostForm)
from connect_db import db
from models import User, Category, Post

admin = Blueprint('adminPanel', __name__, template_folder='templates', static_folder='static')

menu = [
    {"name": "Добавить пост", "url": "adminPanel.show_post"},
    {"name": "Категории", "url": "adminPanel.category"},
    {"name": "Посты", "url": "adminPanel.show_post"},
    {"name": "Профиль", "url": "adminPanel.profile"},
]

last_form = dict()


@admin.route("/")
@admin.route("/profile")
@login_required
def profile():
    form = AddPostForm()
    add_category_choices(form)
    form_u = EditUsernameForm()
    form_e = EditEmailForm()
    form_p = EditPasswordForm()
    l_form = return_last_form()
    return render_template("adminPanel/profile.html",
                           menu=menu, form=form, form_u=form_u, form_e=form_e, form_p=form_p,
                           l_form=l_form, title='Авторизация')


@admin.route("/edit_user", methods=["GET", "POST"])
@login_required
def edit_username():
    if request.method == "POST":
        form = EditUsernameForm(request.form)
        if form.validate_on_submit() and User.query.filter_by(username=form.name.data).first() is None:
            user = User.query.get(current_user.id)
            lost_name = user.username
            user.username = form.name.data
            db.session.add(user)
            db.session.commit()
            flash(f"Логин {lost_name} успешно изменен на {user.username}", category="success")
        else:
            flash(f"Измените логин {form.name.data}. Такой никнейм уже занят", category="error")
    return redirect(url_for('adminPanel.profile'))


@admin.route("/edit_email", methods=["GET", "POST"])
@login_required
def edit_email():
    if request.method == "POST":
        form = EditEmailForm(request.form)
        if form.validate_on_submit() and User.query.filter_by(email=form.email.data).first() is None:
            user = User.query.get(current_user.id)
            lost_email = user.email
            print(f"lost-mail {lost_email}")
            user.email = form.email.data
            db.session.add(user)
            db.session.commit()
            flash(f"E-mail {lost_email} успешно изменен на {user.email}", category="success")
        else:
            flash(f"Измените e-mail {form.email.data}. Такой e-mail уже занят", category="error")
    return redirect(url_for('adminPanel.profile'))


@admin.route("/edit_password", methods=["GET", "POST"])
@login_required
def edit_password():
    if request.method == "POST":
        form = EditPasswordForm(request.form)
        user = User.query.get(current_user.id)
        print(f"password - {user.check_password(form.old_psw.data)}")
        if form.validate_on_submit() and user.check_password(form.old_psw.data):
            try:
                user.set_password(form.new_psw.data)
                db.session.add(user)
                db.session.commit()
                flash(f"Пароль успешно изменен.", category="success")
            except:
                db.session.rollback()
                print("Ошибка записи в БД при изменении пароля. adminPanel.edit_password")
                flash(" записи в БД при изменении пароля.", category="error")
        else:
            flash(f"Неверный пароль. Попробуйте еще раз", category="error")
    return redirect(url_for('adminPanel.profile'))


@admin.route("/delete_profile", methods=["GET", "POST"])
@login_required
def delete_profile():
    if request.method == "POST":
        try:
            user = User.query.get(current_user.id)
            if user.check_password(request.form["psw"]):
                db.session.delete(user)
                db.session.commit()
                logout_user()
                resp = make_response(redirect(url_for("no_authorized")))
                resp.delete_cookie('next')
                print("Пользователь удален")
                flash(f"Пользователь {user.username} успешно удален", category="success")
                return resp
            else:
                flash(f"Неверный пароль. Попробуйте еще раз", category="error")
        except:
            db.session.rollback()
            print("Ошибка удаления из бд. adminPanel.delete_profile")
            flash("Ошибка удаления из бд", category="error")
    return redirect(url_for('adminPanel.profile'))


@admin.route("/category")
@login_required
def category():
    form = AddPostForm()
    add_category_choices(form)
    form_a = EditCategoryForm()
    form_e = EditCategoryForm()
    form_d = DeleteCategoryForm()
    l_form = return_last_form()
    categories = Category.query.all()
    # print(categories)
    open_modal_add_cat = request.cookies.get('open_modal_add_cat')
    resp = make_response(render_template("adminPanel/category.html", menu=menu, form=form, form_a=form_a,
                                         form_e=form_e, form_d=form_d, l_form=l_form, categories=categories,
                                         open_modal_add_cat=open_modal_add_cat, title='Категории'))
    resp.delete_cookie('open_modal_add_cat')
    return resp


@admin.route("/add_category", methods=["GET", "POST"])
@login_required
def add_category():
    if request.method == "POST":
        form_a = EditCategoryForm()
        if form_a.validate_on_submit() and Category.query.filter_by(name=form_a.name.data).first() is None:
            try:
                add_cat = Category(name=form_a.name.data)
                db.session.add(add_cat)
                db.session.commit()
                flash("Категория успешно добавлена", "success")
            except:
                db.session.rollback()
                print("Ошибка добавления в бд")
                flash("Ошибка добавления в бд", category="error")
        else:
            print(f"Категория '{form_a.name.data}' уже есть в БД")
            flash(f"Категория '{form_a.name.data}' уже есть в БД", category="error")

    return redirect(url_for('adminPanel.category'))


@admin.route("/edit_category/<alias>", methods=["GET", "POST"])
@login_required
def edit_category(alias):
    print(alias)
    if request.method == "POST":
        form_e = EditCategoryForm()
        if form_e.validate_on_submit() and Category.query.filter_by(name=form_e.name.data).first() is None:
            try:
                edit_cat = Category.query.filter_by(id=alias).first()
                edit_cat.name = form_e.name.data
                print(f"edit_cat- {edit_cat.name}")
                db.session.add(edit_cat)
                db.session.commit()
                flash("Категория успешно добавлена", "success")
            except:
                db.session.rollback()
                print("Ошибка добавления в бд")
                flash("Ошибка добавления в бд", category="error")
        else:
            print(f"Категория '{form_e.name.data}' уже есть в БД")
            flash(f"Категория '{form_e.name.data}' уже есть в БД", category="error")

    return redirect(url_for('adminPanel.category'))


@admin.route("/delete_category/<alias>", methods=["GET", "POST"])
@login_required
def delete_category(alias):
    if request.method == "POST":
        form_d = DeleteCategoryForm()
        if (form_d.validate_on_submit() and form_d.name.data == "delete"
                and Post.query.filter_by(category_id=alias).first() is None):
            try:
                delete_cat = Category.query.filter_by(id=alias).first()
                db.session.delete(delete_cat)
                db.session.commit()
                flash("Категория успешно удалена", "success")
            except:
                db.session.rollback()
                print("Ошибка удаления категории из бд")
                flash("Ошибка удаления категории из бд", category="error")
        else:
            print(f"Категория '{form_d.name.data}' не удалена из БД. Есть связанные посты")
            flash(f"Категория '{form_d.name.data}' не удалена из БД. Есть связанные посты", category="error")

    return redirect(url_for('adminPanel.category'))


@admin.route('/uploads/<filename>')
@login_required
def send_file(filename):
    return send_from_directory(flask.current_app.config['UPLOAD_FOLDER'], filename)


@admin.route("/show_post")
@login_required
def show_post():
    form = AddPostForm()
    add_category_choices(form)
    l_form = return_last_form()
    posts = Post.query.filter_by(user_id=current_user.id).join(Category).add_columns(Post.title, Post.desc,
                                                                                     Post.filename, Category.name)
    open_modal_add_post = request.cookies.get('open_modal_add_post')
    # print(f'hasattr - {hasattr(g, "last_form")}')

    resp = make_response(
        render_template("adminPanel/post.html", menu=menu, form=form, posts=posts,
                        open_modal_add_post=open_modal_add_post,
                        l_form=l_form, title='Мои посты'))
    resp.delete_cookie('open_modal_add_post')

    print(f'last form - {last_form}')
    print(posts)
    [print(post) for post in posts]
    return resp


@admin.route("/add_post", methods=["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        form = AddPostForm()
        add_category_choices(form)

        if len(form.category.choices) == 1:
            resp = redirect(url_for('adminPanel.category'))
            resp.set_cookie('open_modal_add_cat', 'True')
            flash("Создайте категорию для добавления поста.", category="error")
            return resp
        print(f"form validate - {form.validate_on_submit()}")
        if form.validate_on_submit():
            if not form.category.data:
                resp = redirect(url_for('adminPanel.show_post'))
                resp.set_cookie('open_modal_add_post', 'True')

                global last_form
                last_form = {'title': form.title.data, 'image': form.image.data, 'description': form.description.data,
                             'text': form.text.data}

                flash("Вы не выбрали категорию. Пост не сохранен в БД.", category="error")
                return resp
            try:
                add_post_to_db = Post(title=form.title.data,
                                      category_id=form.category.data,
                                      desc=form.description.data,
                                      post=form.text.data,
                                      user_id=current_user.id
                                      )

                db.session.add(add_post_to_db)
                db.session.commit()

                flash("Пост успешно добавлен", "success")
                if form.image.data:
                    image = form.image.data

                    # Создаю имя файла вида: "image_p"+"post.id" + ".расширение исходного файла"
                    last_part = image.filename.split('.')[-1]
                    filename = secure_filename(f"image_p{add_post_to_db.id}.{last_part}")

                    # Создаю директорию "uploads", если ее нет
                    os.makedirs(flask.current_app.config['UPLOAD_FOLDER'], exist_ok=True)

                    # Сохраняю файл с новым именем в директории "uploads"
                    image.save(os.path.join(flask.current_app.config['UPLOAD_FOLDER'], filename))

                    add_post_to_db.filename = filename
                    db.session.add(add_post_to_db)
                    db.session.commit()
            except:
                db.session.rollback()
                print("Ошибка добавления в бд")
                flash("Ошибка добавления в бд", category="error")

    return redirect(url_for('adminPanel.show_post'))


def add_category_choices(form):
    form.category.choices = [("", "Выберите категорию")]
    form.category.choices += ([(option.id, option.name) for option in Category.query.all()])


def return_last_form():
    global last_form
    l_form = dict()
    print(f'last form - {last_form}')
    if last_form:
        l_form = last_form
        last_form = {}
    return l_form
