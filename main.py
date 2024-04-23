from flask import Flask, render_template
from connect_db import db, login
# from models import User, Post
from authorize.login import user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_site.db'
app.config["SECRET_KEY"] = "wewrtrtey1223345dfgdf"

db.init_app(app)
login.init_app(app)

app.register_blueprint(user, url_prefix="/user")


@app.before_request
def before_request():
    db.create_all()


@app.route("/")
def index():
    # post = Post()
    # user1 = User()
    # post.query.all()
    # user1.query.all()
    # print(f"posts = {post}")
    # print(f"users = {user1}")
    return render_template("index.html", title="Главная")


if __name__ == "__main__":
    app.run(debug=True)
