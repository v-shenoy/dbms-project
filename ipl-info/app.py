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
    if "logged_in" in session and session["logged_in"]:
        return redirect(url_for("index")) 
    elif request.method == "POST" and form.validate():
        username = form.username.data
        password_candidate =str(form.password.data)

        # Create cursor
        cur = mysql.connection.cursor()

        result = cur.execute('''SELECT * FROM users WHERE username = 
        "{}"'''.format(username))

        if result > 0:
            # Get associated data
            data = cur.fetchone()
            password = data["password"]
            if sha256_crypt.verify(password_candidate, password):
                # Create session and redirect to home
                session["logged_in"] = True
                session["username"] = username

                flash("You have now logged in as {}.".format(username), "success")
                return redirect(url_for("index"))
            else:
                # Display incorrect login
                flash("Incorrect password.", "failure")
                return render_template("login.html", form=form)
            cur.close()
        else:
            flash("Username not found.", "failure")
            return render_template("login.html", form=form)
        cur.close()
    return render_template("login.html", form=form)


@app.route("/register", methods = ["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if "logged_in" in session and session["logged_in"]:
        return redirect(url_for("index"))     
    elif request.method == "POST" and form.validate():
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

        flash("You have been registered.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out.", "success")
    return redirect(url_for("index"))


@app.route("/records", methods = ["GET", "POST"])
def records():
    form = request.form
    if request.method == "POST":
        results = None
        # Create connection
        cur = mysql.connection.cursor()
        if form["record"] in ["runs", "hundreds", "fifties", "sixes", "fours"]:
            # Extract information by executing query
            length = cur.execute('''SELECT * FROM players, batsmen WHERE 
            (players.pid = batsmen.pid) ORDER BY {} DESC LIMIT 30'''.format(form["record"]))
            if length > 0:
                results = cur.fetchall()
            flash("Showing results for \"most {}\".".format(form["record"]), "success")
            cur.close();
            return render_template("records.html", form=form, results=results, type="batsmen")    
        elif form["record"] in ["wickets", "economy"]:
            # Extract information by executing query
            order = "DESC"
            if form["record"] == "economy":
                order = "ASC"
            length = cur.execute('''SELECT * FROM players, bowlers WHERE 
            ((players.pid = bowlers.pid) AND overs > 50) ORDER BY {} {} LIMIT 30'''.format(form["record"], order))
            if length > 0:
                results = cur.fetchall()
            if form["record"] == "wickets":
                flash("Showing results for \"most wickets\".", "success")
            else:
                flash("Showing results for \"best economy\".", "success")
            cur.close();
            return render_template("records.html", form=form, results=results, type="bowlers")
        else:
            # Extract information by executing query
            length = cur.execute('''SELECT * FROM teams ORDER BY {} DESC LIMIT 
            30'''.format(form["record"])) 
            if length > 0:
                results = cur.fetchall()
            if form["record"] == "highest":
                flash("Showing results for \"highest score\".", "success")
            else:
                flash("Showing results for \"most wins\".", "success")
            return render_template("records.html", form=form, results=results, type="teams")
    return render_template("records.html", form=form, results=None, type=None)


if __name__ == "__main__":
    app.secret_key = "secret_placeholder_lmao"
    app.run(debug = True)