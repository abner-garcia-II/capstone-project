from dotenv import load_dotenv
import os
import requests
import json
import sqlite3

load_dotenv()

apiKey = os.environ.get('xbl_api_key')
headers = {
    'accept': '/',
    'x-authorization': apiKey
}


def insertXblData(steamID):
    url = f'https://xbl.io/api/v2/search/{steamID}'
    conn = sqlite3.connect('sqlite/main.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS xbl_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gamertag TEXT,
        unique_modern_gamertag TEXT,
        gamerscore TEXT,
        display_pic TEXT,
        follower_count INTEGER,
        following_count INTEGER,
        has_game_pass BOOLEAN
    )
    ''')

    cursor.execute("""DELETE FROM xbl_data WHERE gamerscore >= 0""")

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        print("Full response data (formatted):")
        print(json.dumps(data, indent=4))

        if 'people' in data:
            print("\nParsed relevant data:")
            people = data['people']

            for person in people:
                gamertag = person.get('gamertag', 'N/A')
                unique_modern_gamertag = person.get('uniqueModernGamertag', 'N/A')
                gamerscore = person.get('gamerScore', 'N/A')
                display_pic = person.get('displayPicRaw', 'N/A')
                follower_count = person.get('detail', {}).get('followerCount', 0)
                following_count = person.get('detail', {}).get('followingCount', 0)
                has_game_pass = person.get('detail', {}).get('hasGamePass', False)

                print(f"\nGamertag: {gamertag}")
                print(f"Unique Modern Gamertag: {unique_modern_gamertag}")
                print(f"Gamerscore: {gamerscore}")
                print(f"Display Picture: {display_pic}")
                print(f"Follower Count: {follower_count}")
                print(f"Following Count: {following_count}")
                print(f"Has Game Pass: {has_game_pass}")

                cursor.execute('''
                    INSERT INTO xbl_data (gamertag, unique_modern_gamertag, gamerscore, display_pic, follower_count, following_count, has_game_pass)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (gamertag, unique_modern_gamertag, gamerscore, display_pic, follower_count, following_count, has_game_pass))

            conn.commit()
            print("\nData successfully inserted into the database.")
        else:
            print("No 'people' data found in the response.")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        print(response.text)

    conn.close()

