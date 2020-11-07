from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
import sqlite3 as sql
import random
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "Jahaan"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
#app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = True
#app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = 'kidflash2jahaan@gmail.com'
app.config['MAIL_PASSWORD'] = 'oapbzxnsmqqtjfgz'
app.config['MAIL_DEFAULT_SENDER'] = "kidflash2jahaan@gmail.com"
#app.config['MAIL_MAX_EMAILS'] = 10
# app.config['MAIL_SUPPRESS_SEND'] = False
#app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)

answers = ["It is certain",
           "It is decidedly so",
           "Without a doubt",
           "Yes - definitely",
           "You may rely on it",
           "As I see it, yes",
           "Most likely",
           "Outlook good",
           "Yes",
           "Signs point to yes",
           "Don't count on it",
           "My reply is no",
           "My sources say no",
           "Outlook not so good",
           "Very doubtful",
           "Reply hazy, try again",
           "Ask again later",
           "Better not tell you now",
           "Cannot predict now",
           "Concentrate and ask again"]


@app.route("/magic_8_ball", methods=['GET', 'POST'])
def eight_ball():
    return render_template("Magic_8_ball.html")


@app.route("/magic_8_ball/answer", methods=['GET', 'POST'])
def eight_ball_answer():
    random_c = random.choice(answers)
    return render_template("Magic_8_ball_answer.html", randomc=random_c)


@app.route("/feedback")
def feedback():
    return render_template("Feedback.html")


@app.route("/feedback/send-email", methods=['GET', 'POST'])
def feedback_send_email():
    Name = request.form.get("Name")
    Email = request.form.get("Email")
    Feedback_message = request.form.get("Message")
    Feedback_subject = 'Website feedback from ' + Name + ', ' + Email

    msg = Message(Feedback_subject, sender=Email, recipients=[
                  "jahaan@fireballtechnologies.com"], body=Feedback_message)
    mail.send(msg)
    return "Thank you for your feedback!"


@app.route("/message_codifier/encrypt")
def encrypt():
    return render_template("Encrypt.html")


@app.route("/message_codifier/encrypt/check", methods=['GET', 'POST'])
def encrypt_check():
    message = request.form.get("message")
    e_m = encrypt_message(message)

    return render_template("Encrypt.html", encrypted_message=e_m)


def encrypt_message(message):
    encrypted_message = ""
    for i in message:
        calc1 = ord(i)
        calc2 = calc1 + 5
        calc3 = chr(calc2)
        encrypted_message = encrypted_message + calc3
    return encrypted_message


@app.route("/message_codifier/decrypt")
def decrypt():
    return render_template("Decrypt.html")


@app.route("/message_codifier/decrypt/check", methods=['GET', 'POST'])
def decrypt_check():
    message = request.form.get("message")
    d_m = decrypt_message(message)

    return render_template("Decrypt.html", decrypted_message=d_m)


def decrypt_message(message):
    decrypted_message = ""
    for i in message:
        calc1 = ord(i)
        calc2 = calc1 - 5
        calc3 = chr(calc2)
        decrypted_message = decrypted_message + calc3
    return decrypted_message
@app.route("/")
def redirect_home():
    return redirect("/home")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/show/users", methods=["POST", "GET"])
def show_users():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from user")
    rows = cur.fetchall()
    return render_template("show_users.html", rows=rows)


@app.route("/verify", methods=["POST", "GET"])
def verify():
    username = request.form.get("username")
    password = request.form.get("password")
    return_value = verify_user(username, password)
    if return_value == True:
        session["approved"] = True
        msg = "Operation succesful¢¢¢¢ ({} added)"
        session["username"] = username
        return render_template("control_panel.html", msg=msg)
    else:
        session["approved"] = False
        msg = "Operation unsuccesful ({} not added)"
        return render_template("control_panel.html", msg=msg)


@app.route("/add/users", methods=["POST", "GET"])
def add_user():
    print("creating user", request.method)
    con = ""
    if request.method == "POST":
        try:
            first_name = request.form["firstName"]
            last_name = request.form["lastName"]
            email = request.form["username"]
            password = request.form["password"]
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO user(first_name, last_name, email, password) VALUES(?,?,?,?)",
                            (first_name, last_name, email, password))
                con.commit()
                print("succesfull")
        except:
            con.rollback()
            msg = "Operation unsuccesful¢¢¢¢¢¢¢¢¢¢¢¢¢"
            return render_template("control_panel.html", msg=msg)
        finally:
            con.close()
            msg = "Operation succesful¢¢¢¢¢¢¢¢¢¢¢¢¢¢¢"
            if email == "jahaan@fireballtechnologies.com" and password == "Jahaan09":
                return redirect("/show/users")
            else:
                return redirect("/login")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/create/task")
def create_task():
    return render_template("create_task.html")


@app.route("/create/food")
def create_food():
    return render_template("create_food.html")


@app.route("/add/task", methods=["POST", "GET"])
def add_task():
    print("adding task", request.method)
    con = ""
    if request.method == "POST":
        try:
            task_name = request.form["task_name"]
            priority = request.form["priority"]
            username = session.get("username")
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO To_do_list (task_name,priority,username) VALUES (?,?,?)", (task_name, priority, username))
                con.commit()
        except:
            con.rollback()
            msg = "Operation unsuccesful¢¢¢¢¢¢¢¢¢¢¢¢¢"
            return render_template("control_panel.html", msg=msg)
        finally:
            con.close()
            msg = "Operation succesful¢¢¢¢¢¢¢¢¢¢¢¢¢¢¢"
            return render_template("control_panel.html", msg=msg)


@app.route("/add/food", methods=["POST", "GET"])
def add_food():
    print("adding food", request.method)
    con = ""
    if request.method == "POST":
        try:
            food_name = request.form["food_name"]
            protein = request.form["protein"]
            carbs = request.form["carbs"]
            fat = request.form["fat"]
            username = session.get("username")
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO Food_tracker (food_name,protein,carbs,fat,username) VALUES (?,?,?,?,?)", (food_name, protein, carbs, fat, username))
                con.commit()
        except:
            con.rollback()
            msg = "Operation unsuccesful¢¢¢¢¢¢¢¢¢¢¢¢¢"
            return render_template("control_panel.html", msg=msg)
        finally:
            con.close()
            msg = "Operation succesful¢¢¢¢¢¢¢¢¢¢¢¢¢¢¢"
            return render_template("control_panel.html", msg=msg)


@app.route("/show/list")
def view_list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from To_do_list order by Priority")
    rows = cur.fetchall()
    return render_template("show_list.html", rows=rows)


@app.route("/delete/task")
def delete_task():
    id = request.args.get("id")
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("delete from To_do_list where id = ?", id)
    con.commit()
    msg = "Operation succesful¢¢¢¢¢¢¢¢¢¢¢¢¢¢¢"
    return render_template("control_panel.html", msg=msg)


@app.route("/complete/task")
def complete_task():
    id = request.args.get("id")
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("delete from To_do_list where id = ?", id)
    con.commit()
    msg = "Operation succesful¢¢¢¢¢¢¢¢¢¢¢¢¢¢¢"
    return render_template("control_panel.html", msg=msg)


def verify_user(username, password):
    login_success = False
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    print(username)
    cur = con.cursor()
    cur.execute("select password from user where email = ?", [username])
    rose = cur.fetchall()
    db_password = ""
    for rows in rose:
        db_password = rows[0]
    print(password)
    if db_password == password:
        login_success = True
    else:
        login_success = False
    return login_success


if __name__ == "__main__":
    app.run(debug=True)
