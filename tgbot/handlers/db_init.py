import os

import psycopg2

from tgbot.utils.logger import logger

# Setting up logging


DATABASE_URL = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


def init_db() -> None:
    """Initialize the database and create the tables if they don't exist."""
    with conn.cursor() as cursor:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT,
                username TEXT,
                topic_of_interest TEXT NOT NULL
            );
        """)
    conn.commit()
    logger.info("Database initialized and tables created if not exists.")


if __name__ == "__main__":
    init_db()
