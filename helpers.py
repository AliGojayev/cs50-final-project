from functools import wraps
from sqlite3 import Connection, connect

from cs50 import SQL
from flask import redirect, session


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def snake_to_sentence_case(text):
    """Convert snake case string to sentence case"""
    sentence = text.replace("_", " ").capitalize()

    return sentence


def get_table_columns(
    db: SQL, table: str, excluded_columns: list[str] = []
) -> list[str]:
    """
    Returns list of names of columns that are available in the table,
    excluding specified column names (if provided).
    """
    all_columns = [
        column["name"]
        for column in db.execute("SELECT name FROM pragma_table_info(?);", table)
    ]

    columns = []

    for column in all_columns:
        if column not in excluded_columns:
            columns.append(column)

    return columns


def create_movies_database(db: SQL | Connection):
    db.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        title        TEXT    NOT NULL,
        genre        TEXT    NOT NULL,
        mood         TEXT    NOT NULL,
        image_path   TEXT    NOT NULL DEFAULT '_not-found.jpg',
        description  TEXT    NOT NULL,
        release_year INTEGER NOT NULL,
        rating       REAL    NOT NULL
    );
    """)


def create_users_database(db: SQL | Connection):
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT    NOT NULL UNIQUE,
        hash     TEXT    NOT NULL
    );
    """)


def create_watched_movies_database(db: SQL | Connection):
    db.execute("""
    CREATE TABLE watched_movies (
        user_id  INTEGER NOT NULL,
        movie_id INTEGER NOT NULL,
        rating   REAL,

        PRIMARY KEY (user_id, movie_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (movie_id) REFERENCES movies(id)
    );
    """)


def setup_database(database_path: str) -> None:
    temp_db = connect(database_path)

    create_users_database(temp_db)
    create_movies_database(temp_db)
    create_watched_movies_database(temp_db)

    temp_db.commit()

    del temp_db
