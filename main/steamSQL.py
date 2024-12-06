from dotenv import load_dotenv
import os
import requests
import sqlite3

# Load environment variables
load_dotenv()

apiKey = os.environ.get('STEAM_API_KEY')

def insertSteamData (userSteamID):
    if apiKey is None:
        raise ValueError("API Key not found. Make sure to set the STEAM_API_KEY in your .env file.")

    # Prompt the user to input their SteamID
    steamID = userSteamID#input("Please enter your SteamID: ").strip()

    if not steamID.isdigit():
        raise ValueError("Invalid SteamID. Please enter a numeric SteamID.")

    link = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={apiKey}&steamid={steamID}&format=json&include_appinfo=true'

    response = requests.get(link)

    if response.status_code == 200:
        data = response.json()

        owned_games = data.get('response', {}).get('games', [])

        if owned_games:
            print(f"Owned Games for SteamID {steamID}:")

            # Connect to the existing SQLite database used in riot_sql.py
            conn = sqlite3.connect('sqlite/main.db')  # Assuming the database file is in the 'sqlite' folder
            cursor = conn.cursor()

            # Create table for owned games if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS steam_owned_games (
                steamID TEXT,
                appid INTEGER,
                name TEXT,
                playtime_hours REAL,
                PRIMARY KEY (steamID, appid)
            )
            """)
            
            cursor.execute("""DELETE FROM steam_owned_games WHERE steamID > 0""")

            for game in owned_games:
                game_name = game.get('name', 'Name not available')
                playtime_minutes = game.get('playtime_forever', 0)
                playtime_hours = playtime_minutes / 60  # Convert to hours

                # Insert or replace game data into the steam_owned_games table
                cursor.execute("""
                INSERT OR REPLACE INTO steam_owned_games (steamID, appid, name, playtime_hours)
                VALUES (?, ?, ?, ?)
                """, (steamID, game['appid'], game_name, playtime_hours))

                print(f"- {game_name} (App ID: {game['appid']}), Playtime: {playtime_hours:.2f} hours")

            # Commit changes to the database
            conn.commit()

            print("\nGames have been successfully stored in the SQLite database.")

            # Close the database connection
            cursor.close()
            conn.close()
        else:
            print("No games found for this SteamID.")
    else:
        print(f"Error: {response.status_code} - {response.reason}")
