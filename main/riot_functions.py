from dotenv import load_dotenv
import os
import json
import requests
import sqlite3

load_dotenv()

apiKey = os.environ.get('riot_api_key')

def clearJsonData():
    file = open("JSONs/league-game-data.json", "w")
    file.write("")
    file.close()
    return 0

def clearParsedData():
    file = open("JSONs/league-game-parsed-data.txt", "w")
    file.write("")
    file.close()
    return 0

def clearRawData():
    file = open("JSONs/raw-match-data.txt", "w")
    file.write("")
    file.close()
    return 0

def clearPlayerData():
    file = open("JSONs/league-game-riotids-and-taglines.txt", "w")
    file.write("")
    file.close()
    return 0

def getPuuid(gameNameInput, tagLineInput):
    global gameName 
    gameName = gameNameInput#input("Please enter your game name: ")

    global tagLine 
    tagLine = tagLineInput#input('\nPlease enter your tagline. (The part of your username that comes after the #): ')

    link = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={apiKey}'

    response = requests.get(link)

    if response.status_code == 200:
        global puuid 
        puuid = response.json()['puuid']
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        print(response.text)
    return puuid

def getRegion(regionInput):
    global region 
    region = regionInput#input('\nList of regions: BR1, EUN1, EUW1, JP1, KR, LA1, LA2, ME1, NA1, OC1, PH2, RU, SG2, TH2, TR1, TW2, VN2\nPlease enter the region your account is in: ').upper()
    
    if region in ['BR1', 'LA1', 'LA2', 'NA1']:
        region = 'americas'
    elif region in ['EUN1', 'EUW1', 'ME1', 'RU', 'TR1']:
        region = 'europe'
    elif region in ['JP', 'KR']:
        region = 'asia'
    elif region in ['OC1', 'PH2', 'SG2', 'TH2', 'TW2', 'VN2']:
        region = 'sea'
    return region
        
def getMatchHistoryFromPuuid(gameNameParam, tagLineParam, regionParam, start=0, count=20):
    region = getRegion(regionParam)
    puuid = getPuuid(gameNameParam, tagLineParam)
    
    rooturl = f'https://{region}.api.riotgames.com'
    endpoint = f'/lol/match/v5/matches/by-puuid/{puuid}/ids'
    query_params = f'?start={start}&count={count}'
    global matchId
    matchId = requests.get(rooturl + endpoint + query_params + '&api_key=' + apiKey)
    
    return matchId.json()

def getMatchDataFromId(gameNameParam, tagLineParam, regionParam):
    region = getRegion(regionParam)
    
    match = getMatchHistoryFromPuuid(gameNameParam, tagLineParam, region)
    
    for gameNum in range(0, 20):
        root_url = f'https://{region}.api.riotgames.com'
        endpoint = f'/lol/match/v5/matches/{match[gameNum]}'
        
        response = requests.get(root_url + endpoint + '?api_key=' + apiKey).json()
        data = json.dumps(response, indent=2)
        #specific_data = json.dumps(response["info"]["participants"][1], indent=2)
        with open("JSONs/league-game-data.json", "a") as outfile:
            outfile.write(data)
    outfile.close()

def getPlayers():
    clearPlayerData()
    matchId = getMatchHistoryFromPuuid()
    root_url = f'https://{region}.api.riotgames.com'
    endpoint = f'/lol/match/v5/matches/{matchId}'
    
    response = requests.get(root_url + endpoint + '?api_key=' + apiKey).json()
    file = open("JSONs/league-game-riotids-and-taglines.txt", "w", encoding='utf-8')
    for player in range(0, 10):
        matchData = f'Player {player+1}: {json.dumps(response["info"]["participants"][player]["riotIdGameName"], indent=2).replace('"','')}#{json.dumps(response["info"]["participants"][player]["riotIdTagline"]).replace('"','')}\n'
        file.write(matchData)
    file.close()
    
    return matchData

def getParsedDataToTxt():
    clearParsedData()
    clearJsonData()
    getPuuid()
    getRegion()
    matchId = getMatchHistoryFromPuuid()
    getMatchDataFromId()
    for gameNum in range(0 ,20):
        root_url = f'https://{region}.api.riotgames.com'
        endpoint = f'/lol/match/v5/matches/{matchId[gameNum]}'
        response = requests.get(root_url + endpoint + '?api_key=' + apiKey)
        data = response.json()
        file = open("JSONs/league-game-parsed-data.txt", "a", encoding='utf-8')
        MATCHID = f'{json.dumps(data['metadata']['matchId'], indent=2).replace('"', '')}\n'
        file.write(f'Match ID: {MATCHID}-------------------------\n')
        file.close()
        if response.status_code == 200:
            for player in range (0, 10):
                file2 = open("JSONs/league-game-parsed-data.txt", "a", encoding="utf-8")
                PUUID = f'{json.dumps(data['metadata']['participants'][player], indent=2).replace('"', '')}'
                GAMENAME = f'{json.dumps(data["info"]["participants"][player]["riotIdGameName"], indent=2).replace('"','')}'
                TAGLINE = f'{json.dumps(data["info"]["participants"][player]["riotIdTagline"], indent=2).replace('"','')}'
                POSITION = f'{json.dumps(data["info"]["participants"][player]["teamPosition"], indent=2).replace('"','')}'
                if POSITION == '':
                    POSITION = 'NONE'
                CHAMPIONNAME = f'{json.dumps(data["info"]["participants"][player]["championName"], indent=2).replace('"','')}'
                TEAM = f'{json.dumps(data["info"]["participants"][player]["teamId"], indent=2).replace('"','')}'
                if TEAM == '100':
                    TEAM = 'BLUE'
                elif TEAM == '200':
                    TEAM = 'RED'
                TOTALDMGDEALTTOCHAMPS = f'{json.dumps(data["info"]["participants"][player]["totalDamageDealtToChampions"], indent=2).replace('"','')}'
                matchData = f'Player {player+1}: {PUUID}|{GAMENAME}|{TAGLINE}|{POSITION}|{CHAMPIONNAME}|{TEAM}|{TOTALDMGDEALTTOCHAMPS}\n'
                file2.write(matchData)
            file2.write("\n")
            file2.close()
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            print(response.text)
    return matchData

def getRawMatchDataToTxt():
    clearParsedData()
    clearJsonData()
    getPuuid()
    getRegion()
    matchId = getMatchHistoryFromPuuid()
    getMatchDataFromId()
    for gameNum in range(0 ,20):
        root_url = f'https://{region}.api.riotgames.com'
        endpoint = f'/lol/match/v5/matches/{matchId[gameNum]}'
        response = requests.get(root_url + endpoint + '?api_key=' + apiKey)
        data = response.json()
        file = open("JSONs/league-game-parsed-data.txt", "a", encoding='utf-8')
        MATCHID = f'{json.dumps(data['metadata']['matchId'], indent=2).replace('"', '')}\n'
        file.write(f'Match ID: {MATCHID}-------------------------\n')
        file.close()
        if response.status_code == 200:
            for player in range (0, 10):
                file2 = open("JSONs/league-game-parsed-data.txt", "a", encoding="utf-8")
                PUUID = f'{json.dumps(data['metadata']['participants'][player], indent=2).replace('"', '')}'
                GAMENAME = f'{json.dumps(data["info"]["participants"][player]["riotIdGameName"], indent=2).replace('"','')}'
                TAGLINE = f'{json.dumps(data["info"]["participants"][player]["riotIdTagline"], indent=2).replace('"','')}'
                POSITION = f'{json.dumps(data["info"]["participants"][player]["teamPosition"], indent=2).replace('"','')}'
                if POSITION == '':
                    POSITION = 'NONE'
                CHAMPIONNAME = f'{json.dumps(data["info"]["participants"][player]["championName"], indent=2).replace('"','')}'
                TEAM = f'{json.dumps(data["info"]["participants"][player]["teamId"], indent=2).replace('"','')}'
                if TEAM == '100':
                    TEAM = 'BLUE'
                elif TEAM == '200':
                    TEAM = 'RED'
                TOTALDMGDEALTTOCHAMPS = f'{json.dumps(data["info"]["participants"][player]["totalDamageDealtToChampions"], indent=2).replace('"','')}'
                matchData = f'Player {player+1}: {PUUID}|{GAMENAME}|{TAGLINE}|{POSITION}|{CHAMPIONNAME}|{TEAM}|{TOTALDMGDEALTTOCHAMPS}\n'
                file2.write(matchData)
            file2.write("\n")
            file2.close()
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            print(response.text)
    return matchData

def insertMatchHistoryToDB(gameNameParam, tagLineParam, regionParam):
    clearRawData()
    clearJsonData()
    getPuuid(gameNameParam, tagLineParam)
    region = getRegion(regionParam)
    matchId = getMatchHistoryFromPuuid(gameNameParam, tagLineParam, region)
    getMatchDataFromId(gameNameParam, tagLineParam, region)
    for gameNum in range(0 , 20):
        root_url = f'https://{region}.api.riotgames.com'
        endpoint = f'/lol/match/v5/matches/{matchId[gameNum]}'
        response = requests.get(root_url + endpoint + '?api_key=' + apiKey)
        data = response.json()
        if response.status_code == 200:
            for player in range (0, 10):
                file = open("JSONs/raw-match-data.txt", "a", encoding="utf-8")
                matchPk = f'{json.dumps(data['metadata']['matchId'], indent=2).replace('"', '')}'
                puuId = f'{json.dumps(data['metadata']['participants'][player], indent=2).replace('"', '')}'
                gameNameChar = f'{json.dumps(data["info"]["participants"][player]["riotIdGameName"], indent=2).replace('"','')}'
                tagLineChar = f'{json.dumps(data["info"]["participants"][player]["riotIdTagline"], indent=2).replace('"','')}'
                position = f'{json.dumps(data["info"]["participants"][player]["teamPosition"], indent=2).replace('"','')}'
                if position == '':
                    position = 'NONE'
                elif position == 'UTILITY':
                    position = 'SUPPORT'
                championName = f'{json.dumps(data["info"]["participants"][player]["championName"], indent=2).replace('"','')}'
                teamId = f'{json.dumps(data["info"]["participants"][player]["teamId"], indent=2).replace('"','')}'
                if teamId == '100':
                    teamId = 'BLUE'
                elif teamId == '200':
                    teamId = 'RED'
                totalDmgDealtToChamps = f'{json.dumps(data["info"]["participants"][player]["totalDamageDealtToChampions"], indent=2).replace('"','')}'
                matchData = f'{matchPk}\n{puuId}\n{gameNameChar}\n{tagLineChar}\n{position}\n{championName}\n{teamId}\n{totalDmgDealtToChamps}\n'
                file.write(matchData)
                file.close()
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            print(response.text)

    conn = sqlite3.connect('sqlite/main.db')
    cursor = conn.cursor()
    outfile = open("JSONs/raw-match-data.txt", "r", encoding="utf-8")
    lines = outfile.readlines()
    count = 0
    insertQuery = '''INSERT INTO league_matchdata (matchid, puuid, gamename, tagline, position, champname, teamcolor, totaldmgdealttochamps)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
    deleteQuery = '''DELETE FROM league_matchdata WHERE id > 0'''
    createQuery = '''CREATE TABLE IF NOT EXISTS league_matchdata (id INTEGER PRIMARY KEY, matchid TEXT NOT NULL, puuid TEXT NOT NULL, gamename TEXT NOT NULL, tagline TEXT NOT NULL, 
                    position TEXT NOT NULL, champname TEXT NOT NULL, teamcolor TEXT NOT NULL, totaldmgdealttochamps INTEGER NOT NULL)'''
    cursor.execute(createQuery)
    cursor.execute(deleteQuery)
    for line in lines:
        try:
            if response.status_code == 200:
                matchid = lines[count]
                count += 1
                puuid = lines[count]
                count += 1
                gamename = lines[count]
                count += 1
                tagline = lines[count]
                count += 1
                pos = lines[count]
                count += 1
                champname = lines[count]
                count += 1
                team = lines[count]
                count += 1
                totaldmgdealttochamps = lines[count]
                count += 1
                cursor.execute(insertQuery, (matchid, puuid, gamename, tagline, pos, champname, team, totaldmgdealttochamps))
            else:
                print(f"Failed to retrieve data. Status code: {response.status_code}")
                print(response.text)
        except IndexError:
            print("Data successfully entered into database!")
            conn.commit()
            conn.close()
            break

            
def getMatchHistoryFromDB():
    conn = sqlite3.connect("sqlite/main.db")
    cursor = conn.cursor()
    getQuery = """SELECT matchid, puuid, gamename, tagline, position, champname, teamcolor, totaldmgdealttochamps FROM league_matchdata;"""
    cursor.execute(getQuery)
    sqlData = cursor.fetchall()
    conn.close()
    for entries in range(0, 200):
        for column in range(0, 8):
           sqlList = f'{sqlData[entries][column]}'.strip()
    
    return sqlList