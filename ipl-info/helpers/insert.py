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
        cur.execute('''INSERT INTO batsmen(pid, bat_hand, innings, runs, highest, hundreds, fifties, fours, sixes, average, strike_rate, power_index) 
        VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(row[0], row[1], math.floor(Decimal(row[2])), math.floor(Decimal(row[3])), math.floor(Decimal(row[4])), math.floor(Decimal(row[5])),math.floor(Decimal(row[6])), math.floor(Decimal(row[7])), math.floor(Decimal(row[8])), Decimal(row[9]), Decimal(row[10]), round(Decimal(row[11], 2))))
    
    # Insert bowlers
    csv_f = open("./data/bowlers.csv")
    reader = csv.reader(csv_f, delimiter=",")
    next(reader)
    for row in reader:
        cur.execute('''INSERT INTO bowlers(pid, bowl_skill, overs, wickets, runs, economy, average, maidens, best_figure, four_wicket, power_index) 
        VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(row[0], row[1], math.floor(Decimal(row[2])), math.floor(Decimal(row[3])), math.floor(Decimal(row[4])), round(Decimal(row[5]),2), round(Decimal(row[6]),2), math.floor(Decimal(row[7])), row[9], math.floor(Decimal(row[8])),
        round(Decimal(row[10],2))))

    # Insert teams
    csv_f = open("./data/teams.csv")
    reader = csv.reader(csv_f, delimiter=",")
    next(reader)
    for row in reader:
        cur.execute('''INSERT INTO teams(tid, tname, tcode, matches, wins, highest, lowest, biggest_win, home)
        VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'''.format(row[1], row[2], row[3], math.floor(Decimal(row[4])), math.floor(Decimal(row[5])), row[6], row[7], math.floor(Decimal(row[8])), row[9]))
    mysql.connection.commit()

    # Insert umpires
    csv_f = open("./data/umpires.csv")
    reader = csv.reader(csv_f, delimiter=",")
    next(reader)
    for row in reader:
        cur.execute('''INSERT INTO umpires(uid, uname, country)
        VALUES("{}", "{}", "{}")'''.format(row[1], row[2], row[3]))
    mysql.connection.commit()

    # Insert matches
    csv_f = open("./data/matches.csv")
    reader = csv.reader(csv_f, delimiter=",")
    next(reader)
    c = 0
    for row in reader:
        c += 1
        dob_split = row[1].split("-")
        date = "20" + dob_split[2] + "-" + month_to_num[dob_split[1]] + "-" + dob_split[0]
        app.logger.info(str(c) + ": " + str(row[13]))
        if row[11] == "Tie":
            cur.execute('''INSERT INTO matches(matchid, match_date, team1_id, team2_id, season_id, venue, toss_winner_id, toss_decision, is_superover,
            is_result, is_dwl, win_type, won_by, winner_id, mom_id, f_umpire, s_umpire, city, host) VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", 
            "{}", "{}", "{}", {}, "{}", "{}", "{}", "{}", "{}", "{}")'''.format(row[0], date, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], 
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18]))
        elif row[9] == "0":
            cur.execute('''INSERT INTO matches(matchid, match_date, team1_id, team2_id, season_id, venue, toss_winner_id, toss_decision, is_superover,
            is_result, is_dwl, win_type, won_by, winner_id, mom_id, f_umpire, s_umpire, city, host) VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", 
            "{}", "{}", "{}", {}, {}, {}, "{}", "{}", "{}", "{}")'''.format(row[0], date, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], 
            row[10], row[11], row[12], "NULL", "NULL", row[15], row[16], row[17], row[18]))
        else:
            cur.execute('''INSERT INTO matches(matchid, match_date, team1_id, team2_id, season_id, venue, toss_winner_id, toss_decision, is_superover,
            is_result, is_dwl, win_type, won_by, winner_id, mom_id, f_umpire, s_umpire, city, host) VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", 
            "{}", "{}", "{}", "{}", {}, "{}", "{}", "{}", "{}", "{}")'''.format(row[0], date, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], 
            row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18]))
    mysql.connection.commit()
    return render_template("index.html")