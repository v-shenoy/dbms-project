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
                session["uid"] = data["uid"]

                flash("You have now logged in as {}.".format(username), "success")
                session["answers"] ,session["votes"] = get_answers_and_votes(cur, session['questions'])
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
    session['questions'], session['answers'], session['votes'] = get_random_questions()
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


@app.route("/compare", methods = ["GET", "POST"])
def compare():
    form = request.form
    if request.method == "POST":

        cur = mysql.connection.cursor()
        
        player_type = form["player_type"]
        player1 = form["player1"]
        player2 = form["player2"]

        result1 = None
        result2 = None
        if player_type == "batsman":
            len1 = cur.execute('''SELECT * from players, batsmen WHERE (players.pid = batsmen.pid) 
            AND MATCH(pname) AGAINST(\"{}\")'''.format(player1));
            if len1 > 0:
                result1 = cur.fetchone()
            len2 = cur.execute('''SELECT * from players, batsmen WHERE (players.pid = batsmen.pid) 
            AND MATCH(pname) AGAINST(\"{}\")'''.format(player2));
            if len2 > 0:
                result2 = cur.fetchone()
            cur.close()
            return render_template("compare.html", form=form, result1=result1, result2=result2, type="batsman")            
        else:
            len1 = cur.execute('''SELECT * from players, bowlers WHERE (players.pid = bowlers.pid) 
            AND MATCH(pname) AGAINST(\"{}\")'''.format(player1));
            if len1 > 0:
                result1 = cur.fetchone()
            len2 = cur.execute('''SELECT * from players, bowlers WHERE (players.pid = bowlers.pid) 
            AND MATCH(pname) AGAINST(\"{}\")'''.format(player2));
            if len2 > 0:
                result2 = cur.fetchone()
            cur.close()
            return render_template("compare.html", form=form, result1=result1, result2=result2, type="bowler")            
    return render_template("compare.html", form=form, type=None)

@app.route("/rankings")
def rankings():
    cur = mysql.connection.cursor()

    cur.execute('''SELECT * FROM players, batsmen WHERE (players.pid = batsmen.pid) 
    ORDER BY power_index DESC LIMIT 15''')
    batsmen = cur.fetchall()
    
    cur.execute('''SELECT * FROM players, bowlers WHERE (players.pid = bowlers.pid) 
    ORDER BY power_index DESC LIMIT 15''')
    bowlers = cur.fetchall()
    return render_template("rankings.html", batsmen = batsmen, bowlers = bowlers)

@app.route("/matches", methods = ["GET", "POST"])
def matches():
    form = request.form
    if request.method == "POST":
        cur = mysql.connection.cursor()
        match = None
        length = cur.execute('''SELECT * FROM matches WHERE 
        (season_id = {} AND matchid = {})'''.format(form["season_id"], form["matchid"]))

        if length > 0:
            match = cur.fetchone()
            cur.execute('''SELECT * FROM teams WHERE tid = {}'''.format(match["team1_id"]))
            team_one = cur.fetchone()
            cur.execute('''SELECT * FROM teams WHERE tid = {}'''.format(match["team2_id"]))
            team_two = cur.fetchone()
            cur.execute('''SELECT * FROM umpires WHERE uid = {}'''.format(match["f_umpire"]))
            f_umpire = cur.fetchone()
            cur.execute('''SELECT * FROM umpires WHERE uid = {}'''.format(match["s_umpire"]))
            s_umpire = cur.fetchone()

            winner = None
            mom = None
            toss_winner = None
            if match["toss_winner_id"] == match["team1_id"]:
                toss_winner = team_one
            else:
                toss_winner = team_two
            if match["is_result"] == 1:
                cur.execute('''SELECT * FROM players WHERE pid = {}'''.format(match["mom_id"]))
                mom = cur.fetchone()
                if match["winner_id"] == match["team1_id"]:
                    winner = team_one
                else:
                    winner = team_two
            teams = [team_one, team_two]
            umpires = [f_umpire, s_umpire]
            return render_template("matches.html", form = form, match = match, teams = teams,
            umpires = umpires, toss_winner = toss_winner, winner = winner, mom = mom)
        else:
            return render_template("matches.html", form=form, match = match)
    return render_template("matches.html", form=form, match = -1)

@app.route("/submit", methods = ["POST"])
def submit():
    form = request.form
    if ("logged_in" not in session) or (session["logged_in"] == False):
        return redirect(url_for("login"))
    else:
        qid = form["question"]
        value = form[qid]
        cur = mysql.connection.cursor()
        try:
            cur.execute('''INSERT INTO answers(qid, uid, value) VALUES({}, {}, '{}')'''.format(qid, session["uid"], value))
            mysql.connection.commit()
            session["answers"] ,session["votes"] = get_answers_and_votes(cur, session['questions'])
            return redirect(url_for("index"))
        except:
            session["answers"] ,session["votes"] = get_answers_and_votes(cur, session['questions'])
            cur.close()
            return redirect(url_for("index"))

@app.route("/change", methods = ["POST"])
def change():
    session['questions'], session['answers'], session['votes'] = get_random_questions()
    url = request.referrer.split("/")[-1]
    if url != "":
        return redirect(url_for(url))
    else:
        return redirect(url_for("index"))
                
@app.before_first_request
def before_first():
    session['questions'], session['answers'], session['votes'] = get_random_questions()

def get_random_questions():
    cur = mysql.connection.cursor()    
    cur.execute('''SELECT * FROM questions ORDER BY RAND() LIMIT 4''')
    questions = cur.fetchall()
    
    answers, votes = get_answers_and_votes(cur, questions)
    cur.close()
    return questions, answers, votes

def get_answers_and_votes(cur, questions):
    votes = []
    answers = []
    for i in range(4):
        if ("logged_in" in session) and (session["logged_in"] == True):
            length = cur.execute('''SELECT * FROM answers WHERE (qid = {} AND uid = {})'''.format(questions[i]["qid"], session["uid"]))
            if length > 0:
                value = cur.fetchone()["value"]
                cur.execute('''SELECT * FROM questions WHERE (qid = {})'''.format(questions[i]["qid"]))
                ans = cur.fetchone()[value]
                answers.append(ans)
            else:
                answers.append(None)
            question_votes = []
            letters = ['a', 'b', 'c', 'd']
            for letter in letters:
                question_votes.append(cur.execute('''SELECT * FROM answers WHERE (qid = {} AND 
                value = "{}")'''.format(questions[i]["qid"], 'q' + letter)))
                
            total_votes = sum(question_votes)
            if total_votes != 0:
                for i in range(4):
                    question_votes[i] = round((question_votes[i]/total_votes)*100, 2)
            votes.append(question_votes)
        else:
            answers.append(None)     
    app.logger.info(answers)
    app.logger.info(votes)   
    return answers, votes

if __name__ == "__main__":
    app.secret_key = "secret_placeholder_lmao"
    app.run(debug = True)