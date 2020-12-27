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
@app.route("/home")
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
        session["user"] = request.form["name"]
        return redirect(url_for("home"))
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
            return redirect(url_for("home"))
        else:
            return redirect("/login")
    return render_template("login.html", user=user)


@app.route("/ask")
def ask():
    user = get_current_user()
    db = get_db()
    if request.method == "POST":
        db.execute("insert into questions(question_text, asked_by_id, expert_id) values=(?,?,?)",
                   request.form["question"], user["id"], request.form["expert_id"])
        db.commit()
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
    db = get_db()
    users_cur = db.execute(
        "select id, name_text, expert_boolean, admin_boolean from users")
    users_results = users_cur.fetchall()
    return render_template("users.html", user=user, users=users_results)


@app.route("/promote/<user_id>")
def promote(user_id):
    db = get_db()
    db.execute("update users set expert_boolean = 1 where id = ?", [user_id])
    db.commit()
    return redirect(url_for("users"))


@app.route("/demote/<user_id>")
def demote(user_id):
    db = get_db()
    db.execute("update users set expert_boolean = 0 where id = ?", [user_id])
    db.commit()
    return redirect(url_for("users"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
