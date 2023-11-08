import os

import psycopg2

from tgbot.utils.logger import logger

DATABASE_URL = os.environ.get("DATABASE_URL")


def init_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    with conn.cursor() as cursor:
        # Create a table to store user data
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_data (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                topic TEXT,
                description TEXT,
                frequency TEXT,
                persona TEXT,
                level TEXT
            )
        """
        )

    conn.commit()
    logger.info("Database initialized and table created if not exists.")
    conn.close()


def store_user_data(user_id, data):
    """
    Stores or updates user data in the database.

    This function connects to the PostgreSQL database using psycopg2 and either inserts new user data
    or updates existing data if the user_id already exists in the database. It uses an UPSERT operation
    (INSERT ... ON CONFLICT DO UPDATE) to achieve this.

    Parameters:
    - user_id: The unique identifier of the user.
    - data: A dictionary containing the user's data. Expected keys are:
        - "NAME": The name of the user.
        - "TOPIC": The main topic of interest for the user.
        - "DESCRIPTION": A short description or additional details related to the user's topic of interest.
        - "FREQUENCY": How often the user wishes to receive updates or advice.
        - "PERSONA": The type of persona the user has chosen for interaction.
        - "LEVEL": The level of expertise or depth of content the user has requested.

    The function commits the transaction and closes the connection to the database after the operation is complete.
    """

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")

    with conn.cursor() as cursor:
        # Perform an UPSERT operation: insert new data or update existing data based on user_id
        cursor.execute(
            """
            INSERT INTO user_data (user_id, name, topic, description, frequency, persona, level)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE 
            SET name = EXCLUDED.name,
                topic = EXCLUDED.topic,
                description = EXCLUDED.description,
                frequency = EXCLUDED.frequency,
                persona = EXCLUDED.persona,
                level = EXCLUDED.level
        """,
            (
                user_id,
                data["NAME"],
                data["TOPIC"],
                data["DESCRIPTION"],
                data["FREQUENCY"],
                data["PERSONA"],
                data["LEVEL"],
            ),
        )

    # Commit the transaction and close the database connection
    conn.commit()
    conn.close()


def get_user_preferences(user_id):
    """
    Retrieves user preferences from the database based on user_id.
    """
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT name, topic, description, frequency, persona, level FROM user_data WHERE user_id = %s
        """,
            (user_id,),
        )  # Use %s as the placeholder

        user_preferences = cursor.fetchone()

        if user_preferences:
            return {
                "NAME": user_preferences[0],
                "TOPIC": user_preferences[1],
                "DESCRIPTION": user_preferences[2],
                "FREQUENCY": user_preferences[3],
                "PERSONA": user_preferences[4],
                "LEVEL": user_preferences[5],
            }
        else:
            return None
    finally:
        cursor.close()
        conn.close()
