from flask import (Flask, render_template, flash, redirect, url_for, session, 
                    request, logging)
from flask_mysqldb import MySQL 
from passlib.hash import sha256_crypt

from forms import RegisterForm, LoginForm

app = Flask(__name__)

# Configure MySQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "viggy2698"
app.config["MYSQL_DB"] = "iplinfo"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# Init MySQL
mysql = MySQL(app)

# Setup routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        pass
    return render_template("login.html", form=form)

@app.route("/register", methods = ["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute Query
        cur.execute('''INSERT INTO users(name, email, username, password) 
        VALUES("{}", "{}", "{}", "{}")'''.format(name, email, username, password))

        # Commit to database
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash("You have been registered", "success")
        return redirect(url_for("index"))
    return render_template("register.html", form=form)

if __name__ == "__main__":
    app.secret_key = "secret_placeholder_lmao"
    app.run(debug = True)