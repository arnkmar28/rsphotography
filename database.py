import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g
import config

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(config.DATABASE_URL, cursor_factory=RealDictCursor)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    from flask import current_app
    # Ensure tables exist
    # Note: In production, use migrations (Alembic). This is a simple init for the MVP.
    try:
        conn = psycopg2.connect(config.DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id SERIAL PRIMARY KEY,
                public_id TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized.")
    except Exception as e:
        print(f"Error initializing database: {e}")

