import sqlite3
import requests
import json
import sys
import os
from riot_functions import *

#Any commented code is code that I'm working on to make the db not put in any repeat code, however I'm struggling with this. Since no row is unique other than the PK which is just
#an auto incremented primary key that isn't really reliant for checking for repeats I may have to just switch from displaying someone's match history to displaying someone's stats.

#If you wish to test this code, you may run it and use some of the sample accounts I have provided here. The # separates the game name and tagline and the region is expressed as two
#capital letters (the regions abbreviation) followed with either a number or no number depending on the region.

#List of sample accounts:
#deadlyblank#blank NA1
#One Armed Tiger#111 NA1
#Ivern#Treee NA1
#Extreme#8574 NA1
#Hide on bush#KR1 KR
#Pollu#0107 KR
#AITOP#6031 KR
#T1 Gumayusi#KR1 KR
#zJyy#yyy EUW1
#yukino cat#666 EUW1
#xKensuke#1453 EUW1
#Muzan#1996 EUW1

clearRawData()
clearJsonData()
getPuuid()
region = getRegion()
matchId = getMatchHistoryFromPuuid()
getRecentMatchDataFromId()
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
dropQuery = '''DROP TABLE IF EXISTS league_matchdata'''
createQuery = '''CREATE TABLE league_matchdata (id INTEGER PRIMARY KEY, matchid TEXT NOT NULL, puuid TEXT NOT NULL, gamename TEXT NOT NULL, tagline TEXT NOT NULL, 
                 position TEXT NOT NULL, champname TEXT NOT NULL, teamcolor TEXT NOT NULL, totaldmgdealttochamps INTEGER NOT NULL)'''
cursor.execute(dropQuery)
cursor.execute(createQuery)
conn.commit()
for line in lines:
    if response.status_code == 200:
        matchid = lines[count].strip()
        count += 1
        puuid = lines[count].strip()
        count += 1
        gamename = lines[count].strip()
        count += 1
        tagline = lines[count].strip()
        count += 1
        pos = lines[count].strip()
        count += 1
        champname = lines[count].strip()
        count += 1
        team = lines[count].strip()
        count += 1
        totaldmgdealttochamps = lines[count].strip()
        count += 1
        cursor.execute(insertQuery, (matchid, puuid, gamename, tagline, pos, champname, team, totaldmgdealttochamps))
        conn.commit()
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        print(response.text)