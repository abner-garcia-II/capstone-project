from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from riot_functions import *
from steamSQL import *
from xbox_live_api import *

app = Flask(__name__, template_folder="templates")

def getDbConn():
    conn = sqlite3.connect("sqlite/main.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")
    

@app.route("/riot", methods=['GET'])
def new_riot_user():
    msg = ""
    if request.method == 'POST':
        try:
            msg = "Match History Successfully Fetched! Displaying now."
            
        except:
            msg = "Oops! Something went wrong! Please check to make sure all fields were entered in correctly."
    return render_template("riot.html", msg=msg)

@app.route("/steam", methods=['GET', 'POST'])
def get_steam_data():
    msg = "Please enter a numeric value for the steam ID."
    if request.method == 'POST':
        try:
            SteamID = request.form['steamid']
            insertSteamData(SteamID)
            msg = "Games successfully retrieved!"
            
        except ValueError:
            msg = "Please enter a numeric value for the steam ID."
    conn = getDbConn()
    steamData = conn.execute('SELECT * from steam_owned_games').fetchall()
    conn.close()
    return render_template('steam.html', games=steamData, msg=msg)

@app.route("/fortnite", methods=['GET', 'POST'])
def get_fortnite_data():
    conn = getDbConn()
    fortniteData = conn.execute('SELECT * from stats').fetchall()
    conn.close()
    return render_template('fortnite.html', stats=fortniteData)

@app.route("/xbl", methods=['GET', 'POST'])
def get_xbl_data():
    #if request.method == 'POST':
    GamerTag = 'IM0HIMI'
    insertXblData(GamerTag)
    conn = getDbConn()
    xblData = conn.execute('SELECT gamertag, unique_modern_gamertag, gamerscore, follower_count, following_count, has_game_pass FROM xbl_data').fetchall()
    conn.close()
    return render_template('xbl.html', profiles=xblData)

@app.route("/lol_match_history", methods = ['POST', 'GET'])
def get_riot_data():
    msg = ""
    if request.method == 'POST':
        try:
            GameName = request.form['gamename']
            Tagline = request.form['tagline']
            Region = request.form['region']
            
            insertMatchHistoryToDB(GameName, Tagline, Region)
            msg = "Match History Successfully Fetched! Displaying now."
        except:
            msg = "ERROR: Match History was unable to be fetched. Please check to make sure all fields were entered in correctly."
    conn = getDbConn()
    riotData = conn.execute('SELECT gamename, tagline, position, champname, teamcolor, totaldmgdealttochamps FROM league_matchdata').fetchall()
    conn.close()
    return render_template('lol_match_history.html', matches=riotData, msg=msg)
        

if __name__ == "__main__":
    app.run(debug=True)
