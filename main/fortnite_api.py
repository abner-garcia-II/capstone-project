import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get('fn_api_key')

# Constants

USERNAME = input('Please Enter User Name: ')
PLATFORM = 'epic'
URL = "https://fortnite-api.com/v2/stats/br/v2"

# Headers
headers = {
    'Authorization': API_KEY
}

# Parameters
params = {
    'accountType': PLATFORM,
    'timeWindow': 'lifetime',
    'name': USERNAME
}

# Connect to SQLite database
conn = sqlite3.connect('sqlite/main.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS stats (
        username TEXT,
        score INTEGER,
        matches INTEGER,
        winRate REAL,
        kdRatio REAL
    )
''')

# Fetch data from API
response = requests.get(URL, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    stats = data['data']['stats']['all']['overall']
    
    # Prepare data for insertion
    username = USERNAME
    score = stats['score']
    matches = stats['matches']
    winRate = stats['winRate']
    kdRatio = stats['kd']
    
    # SQL query for inserting data
    query = '''INSERT INTO stats (username, score, matches, winRate, kdRatio)
               VALUES (?, ?, ?, ?, ?)'''
    
    # Execute the query and commit changes
    cursor.execute(query, (username, score, matches, winRate, kdRatio))
    conn.commit()
    print("Data inserted successfully!")
else:
    print("Failed to retrieve data:", response.status_code)

# Close the connection
conn.close()
