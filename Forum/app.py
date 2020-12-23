from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db
import os
app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


def get_current_user():
    user_result = None
    if "user" in session:
        user = session["user"]
        db = get_db()
        user_cur = db.execute(
            "select id, name_text, password_text, expert_boolean, admin_boolean from users where name_text = ?", [user])
        user_result = user_cur.fetchone()
    return user_result


@app.route("/")
def home():
    user = get_current_user()
    return render_template("home.html", user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    user = get_current_user()
    if request.method == "POST":
        db = get_db()
        hash_password = generate_password_hash(
            request.form["password"], method="sha256")
        db.execute("insert into users(name_text, password_text, expert_boolean, admin_boolean) values(?,?,?,?)", [
                   request.form["name"], hash_password, "0", "0"])
        db.commit()
        return redirect("/login")
    return render_template("register.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    user = get_current_user()
    if request.method == "POST":
        db = get_db()
        name = request.form["name"]
        password = request.form["password"]
        user_cur = db.execute(
            "select id, name_text, password_text from users where name_text=?", [name])
        user_result = user_cur.fetchone()
        if check_password_hash(user_result["password_text"], password):
            session["user"] = user_result["name_text"]
            return redirect("/")
        else:
            return redirect("/login")
    return render_template("login.html", user=user)


@app.route("/ask")
def ask():
    user = get_current_user()
    return render_template("ask.html", user=user)


@app.route("/question")
def question():
    user = get_current_user()
    return render_template("question.html", user=user)


@app.route("/unanswered")
def unanswered():
    user = get_current_user()
    return render_template("unanswered.html", user=user)


@app.route("/answer")
def answer():
    user = get_current_user()
    return render_template("answer.html", user=user)


@app.route("/users")
def users():
    user = get_current_user()
    return render_template("users.html", user=user)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
