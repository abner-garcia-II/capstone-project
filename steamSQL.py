from dotenv import load_dotenv
import os
import requests
import sqlite3

load_dotenv()

apiKey = os.environ.get('STEAM_API_KEY')

if apiKey is None:
    raise ValueError("API Key not found. Make sure to set the STEAM_API_KEY in your .env file.")

steamID = '76561198142725355'  # My SteamID

link = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={apiKey}&steamid={steamID}&format=json&include_appinfo=true'

response = requests.get(link)

if response.status_code == 200:
    data = response.json()

    owned_games = data.get('response', {}).get('games', [])

    if owned_games:
        print(f"Owned Games for SteamID {steamID}:")

        # Define the path to the SQLite database file
        db_path = os.path.join("sqlite", "main.db")

        # Connect to SQLite using the database path
        db = sqlite3.connect(db_path)
        cursor = db.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS owned_games (
            steamID TEXT,
            appid INTEGER,
            name TEXT,
            playtime_hours REAL,
            PRIMARY KEY (steamID, appid)
        )
        """)

        for game in owned_games:
            game_name = game.get('name', 'Name not available')
            playtime_minutes = game.get('playtime_forever', 0)
            playtime_hours = playtime_minutes / 60

            # Insert or replace game data
            cursor.execute("""
            INSERT OR REPLACE INTO owned_games (steamID, appid, name, playtime_hours)
            VALUES (?, ?, ?, ?)
            """, (steamID, game['appid'], game_name, playtime_hours))

            print(f"- {game_name} (App ID: {game['appid']}), Playtime: {playtime_hours:.2f} hours")

        # Commit changes
        db.commit()

        print("\nGames have been successfully stored in the SQLite database.")

        # Retrieve and print stored games
        cursor.execute("SELECT name, appid, playtime_hours FROM owned_games WHERE steamID = ?", (steamID,))
        for (name, appid, playtime_hours) in cursor.fetchall():
            print(f"- {name} (App ID: {appid}), Playtime: {playtime_hours:.2f} hours")

        # Close the database connection
        cursor.close()
        db.close()
    else:
        print("No games found.")
else:
    print(f"Error: {response.status_code} - {response.reason}")
