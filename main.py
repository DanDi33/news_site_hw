import flask
from flask import Flask, render_template, make_response, request
from connect_db import db, login
from models import User
from authorize.login import user
from adminpanel.admin import admin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_site.db'
app.config["SECRET_KEY"] = "wewrtrtey1223345dfgdf"
app.config['UPLOAD_FOLDER'] = 'uploads'

db.init_app(app)
login.init_app(app)

login.login_view = 'no_authorized'
login.login_message = 'Авторизируетесь для доступа к закрытым страницам'
login.login_message_category = 'success'

app.register_blueprint(user, url_prefix="/user")
app.register_blueprint(admin, url_prefix="/admin")


@login.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.before_request
def before_request():
    db.create_all()


@app.route("/")
def index():
    print(flask.session)
    print(flask.session.get('next'))
    # post = Post()
    # user1 = User()
    # post.query.all()
    # user1.query.all()
    # print(f"posts = {post}")
    # print(f"users = {user1}")
    return render_template("index.html", title="Главная")


@app.route('/no_authorized')
def no_authorized():
    resp = make_response(render_template("no_authorized.html", title="Авторизуйтесь"))
    if request.args.get('next'):
        resp.set_cookie('next', request.args.get('next'))
    return resp


if __name__ == "__main__":
    app.run(debug=True)
