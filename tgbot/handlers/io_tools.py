import os
import sqlite3

DATABASE_URL = os.environ.get("DATABASE_URL")


def init_db():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Create a table to store user data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            topic TEXT,
            frequency TEXT,
            persona TEXT,
            level TEXT
        )
    """)

    conn.commit()
    conn.close()


def store_user_data(user_id, data):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Insert or replace user data
    cursor.execute("""
        INSERT OR REPLACE INTO user_data (user_id, name, topic, frequency, persona, level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, data["NAME"], data["TOPIC"], data["FREQUENCY"], data["PERSONA"], data["LEVEL"]))

    conn.commit()
    conn.close()
