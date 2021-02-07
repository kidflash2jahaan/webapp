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
    db = get_db()
    questions_cur = db.execute('''
                                    select
                                    questions.id as question_id, 
                                    questions.question_text, 
                                    askers.name_text as asker_name, 
                                    experts.name_text as expert_name 
                                    from questions 
                                    join users as askers on askers.id = questions.asked_by_id
                                    join users as experts on experts.id = questions.expert_id 
                                    where questions.answer_text is not null order by questions.id desc''')
    questions_result = questions_cur.fetchall()
    return render_template("home.html", user=user, question=questions_result)


@app.route("/register", methods=["GET", "POST"])
def register():
    user = get_current_user()
    if request.method == "POST":
        db = get_db()
        existing_user_cur = db.execute("select id from users where name_text = ?", [request.form["name"]])
        existing_user = existing_user_cur.fetchone()
        if existing_user:
            return render_template("register.html", user=user, error="User already exists")
        hash_password = generate_password_hash(request.form["password"], method="sha256")
        db.execute("insert into users(name_text, password_text, expert_boolean, admin_boolean) values(?,?,?,?)", [
                   request.form["name"], hash_password, "0", "0"])
        db.commit()
        session["user"] = request.form["name"]
        return redirect(url_for("home"))
    return render_template("register.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    user = get_current_user()
    error = None
    if request.method == "POST":
        db = get_db()
        name = request.form["name"]
        password = request.form["password"]
        user_cur = db.execute(
            "select id, name_text, password_text from users where name_text=?", [name])
        user_result = user_cur.fetchone()
        if user_result:
            if check_password_hash(user_result["password_text"], password):
                session["user"] = user_result["name_text"]
                return redirect(url_for("home"))
            else:
                error="Password is invalid"
        else:
            error="Username is invalid"
    return render_template("login.html", user=user, error=error)

@app.route("/question/<question_id>")
def question(question_id):
    user = get_current_user()
    db = get_db()
    print("question", question_id)
    question_cur = db.execute("""
                                select
                                questions.question_text, 
                                questions.answer_text, 
                                askers.name_text as asker_name, 
                                experts.name_text as expert_name 
                                from questions 
                                join users as askers on askers.id = questions.asked_by_id 
                                join users as experts on experts.id = questions.expert_id 
                                where questions.id = ? 
                                """, [question_id])
    question = question_cur.fetchone()
    print(question)
    return render_template("question.html", user=user, question=question)

@app.route("/ask", methods=["POST", "GET"])
def ask():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    db = get_db()
    if request.method == "POST":
        db.execute("insert into questions(question_text, asked_by_id, expert_id) values(?,?,?)",
                   [request.form["question"], user["id"], request.form["expert"]])
        db.commit()
        redirect(url_for("home"))
    expert_cur = db.execute(
        "select id, name_text from users where expert_boolean = 1")
    expert_results = expert_cur.fetchall()
    return render_template("ask.html", user=user, experts=expert_results)


@app.route("/unanswered")
def unanswered():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    if user["expert_boolean"] == 0:
        return redirect(url_for("home"))
    db = get_db()
    question_cur = db.execute("""
                                select 
                                questions.id, 
                                questions.question_text, 
                                users.name_text 
                                from questions 
                                join users on users.id = questions.asked_by_id 
                                where questions.answer_text is null and questions.expert_id = ?""", [user["id"]])
    questions = question_cur.fetchall()
    return render_template("unanswered.html", user=user, questions=questions)

@app.route("/answer/<question_id>", methods=["GET", "POST"])
def answer(question_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    if user["expert_boolean"] == 0:
        return redirect(url_for("home"))
    db = get_db()
    print("answer route1")
    if request.method == "POST":
        db.execute("update questions set answer_text = ? where id = ?", [
                   request.form["answer_text"], question_id])
        db.commit()
        print("answer route2")
        return redirect(url_for("unanswered"))
    question_cur = db.execute(
        "select id, question_text from questions where id = ?", [question_id])
    question = question_cur.fetchone()
    return render_template("answer.html", user=user, question=question)


@app.route("/users")
def users():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    if user["admin_boolean"] == 0:
        return redirect(url_for("home"))
    db = get_db()
    users_cur = db.execute(
        "select id, name_text, expert_boolean, admin_boolean from users")
    users_results = users_cur.fetchall()
    return render_template("users.html", user=user, users=users_results)


@app.route("/promote/<user_id>")
def promote(user_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    if user["admin_boolean"] == 0:
        return redirect(url_for("home"))
    db = get_db()
    db.execute("update users set expert_boolean = 1 where id = ?", [user_id])
    db.commit()
    return redirect(url_for("users"))


@app.route("/demote/<user_id>")
def demote(user_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    if user["admin_boolean"] == 0:
        return redirect(url_for("home"))
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
