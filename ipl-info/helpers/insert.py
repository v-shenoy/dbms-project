import csv, math
from decimal import Decimal

month_to_num = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}

@app.route("/insert")
def insert():   
    cur = mysql.connection.cursor()

    # Insert players
    csv_f = open("./data/players.csv")
    reader = csv.reader(csv_f, delimiter=",")
    next(reader)
    for row in reader:
        pid = row[1]
        pname = row[2]
        country = row[3]
        dob_split = row[4].split("-")
        dob = "19" + dob_split[2] + "-" + month_to_num[dob_split[1]] + "-" + dob_split[0]
        matches = row[5]
        cur.execute('''INSERT INTO players(pid, pname, country, dob, matches) 
        VALUES("{}", "{}", "{}", "{}", "{}")'''.format(pid, pname, country, dob, matches))

    # Insert batsmen
    csv_f = open("./data/batsmen.csv")
    reader = csv.reader(csv_f, delimiter=",")
    next(reader)
    for row in reader:
        cur.execute('''INSERT INTO batsmen(pid, bat_hand, innings, runs, highest, hundreds, fifties, fours, sixes, average, strike_rate) 
        VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(row[0], row[1], math.floor(Decimal(row[2])), math.floor(Decimal(row[3])), math.floor(Decimal(row[4])),
        math.floor(Decimal(row[5])),math.floor(Decimal(row[6])), math.floor(Decimal(row[7])), math.floor(Decimal(row[8])), Decimal(row[9]), Decimal(row[10])))
    
    # Insert bowlers
    csv_f = open("./data/bowlers.csv")
    reader = csv.reader(csv_f, delimiter=",")
    next(reader)
    for row in reader:
        cur.execute('''INSERT INTO bowlers(pid, bowl_skill, overs, wickets, runs, economy, average, maidens, best_figure, four_wicket) 
        VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(row[0], row[1], math.floor(Decimal(row[2])), math.floor(Decimal(row[3])), math.floor(Decimal(row[4])), round(Decimal(row[5]),2), round(Decimal(row[6]),2), math.floor(Decimal(row[7])), row[9], math.floor(Decimal(row[8]))))

    # Insert teams
    csv_f = open("./data/teams.csv")
    reader = csv.reader(csv_f, delimiter=",")
    next(reader)
    for row in reader:
        cur.execute('''INSERT INTO teams(tid, tname, tcode, matches, wins, highest, lowest, biggest_win, home)
        VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(row[1], row[2], row[3], math.floor(Decimal(row[4])), math.floor(Decimal(row[5])), row[6], row[7], math.floor(Decimal(row[8])), row[9]))
    mysql.connection.commit()
    cur.close()
    return render_template("index.html")