from dotenv import load_dotenv
import os
import json
import requests

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

def getPuuid():
    global gameName 
    gameName = input("Please enter your game name: ")

    global tagLine 
    tagLine = input('\nPlease enter your tagline. (The part of your username that comes after the #): ')

    link = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={apiKey}'

    response = requests.get(link)

    if response.status_code == 200:
        global puuid 
        puuid = response.json()['puuid']
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        print(response.text)
    return puuid

def getRegion():
    global region 
    region = input('\nList of regions: BR1, EUN1, EUW1, JP1, KR, LA1, LA2, ME1, NA1, OC1, PH2, RU, SG2, TH2, TR1, TW2, VN2\nPlease enter the region your account is in: ').upper()
    
    if region in ['BR1', 'LA1', 'LA2', 'NA1']:
        region = 'americas'
    elif region in ['EUN1', 'EUW1', 'ME1', 'RU', 'TR1']:
        region = 'europe'
    elif region in ['JP', 'KR']:
        region = 'asia'
    elif region in ['OC1', 'PH2', 'SG2', 'TH2', 'TW2', 'VN2']:
        region = 'sea'
    return region
        
def getMatchHistoryFromPuuid(start=0, count=20):
    
    rooturl = f'https://{region}.api.riotgames.com'
    endpoint = f'/lol/match/v5/matches/by-puuid/{puuid}/ids'
    query_params = f'?start={start}&count={count}'
    global matchId
    matchId = requests.get(rooturl + endpoint + query_params + '&api_key=' + apiKey)
    
    return matchId.json()

def getRecentMatchDataFromId():
    
    match = getMatchHistoryFromPuuid()[0]
    
    root_url = f'https://{region}.api.riotgames.com'
    endpoint = f'/lol/match/v5/matches/{match}'
    
    response = requests.get(root_url + endpoint + '?api_key=' + apiKey).json()
    data = json.dumps(response, indent=2)
    #specific_data = json.dumps(response["info"]["participants"][1], indent=2)
    with open("JSONs/league-game-data.json", "w") as outfile:
        outfile.write(data)

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
    getRecentMatchDataFromId()
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
    getRecentMatchDataFromId()
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