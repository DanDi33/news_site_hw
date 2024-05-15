from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user, logout_user

from adminpanel.useful.forms import EditUsernameForm, EditEmailForm, EditPasswordForm, EditCategoryForm, \
    DeleteCategoryForm, AddPostForm
from connect_db import db
from models import User, Category, Post

admin = Blueprint('adminPanel', __name__, template_folder='templates', static_folder='static')

menu = [
    {"name": "Добавить пост", "url": "adminPanel.show_post"},
    {"name": "Категории", "url": "adminPanel.category"},
    {"name": "Посты", "url": "adminPanel.show_post"},
    {"name": "Профиль", "url": "adminPanel.profile"},
]


@admin.route("/")
@admin.route("/profile")
@login_required
def profile():
    form = AddPostForm()
    add_category_choices(form)
    form_u = EditUsernameForm()
    form_e = EditEmailForm()
    form_p = EditPasswordForm()
    return render_template("adminPanel/profile.html",
                           menu=menu, form=form, form_u=form_u, form_e=form_e, form_p=form_p, title='Авторизация')


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
    categories = Category.query.all()
    # print(categories)
    return render_template("adminPanel/category.html", menu=menu, form=form, form_a=form_a,
                           form_e=form_e, form_d=form_d, categories=categories, title='Категории')


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


@admin.route("/show_post")
@login_required
def show_post():
    form = AddPostForm()
    add_category_choices(form)

    return render_template("adminPanel/post.html", menu=menu, form=form, title='Добавление поста')


@admin.route("/add_post", methods=["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        form = AddPostForm(request.form)
        add_category_choices(form)
        print(f"Privet {form.validate_on_submit()}")
        if form.validate_on_submit():
            print(form)
        print(form.title.data)
        print(form.category.data)
        print(form.description.data)
        print(form.image.data)
        print(form.text.data)
    return redirect(url_for('adminPanel.show_post'))


def add_category_choices(form):
    form.category.choices = [(0, "Выберите категорию")]
    form.category.choices += ([(option.id, option.name) for option in Category.query.all()])
