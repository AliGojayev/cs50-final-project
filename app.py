from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///database.db")

# @app.after_request
# def after_request(response):
#     """Ensure responses aren't cached"""
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response


def create_movies_database(db: SQL):
    db.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id           INT  PRIMARY KEY AUTO_INCREMENT,
        title        TEXT NOT NULL,
        genre        TEXT NOT NULL,
        mood         TEXT NOT NULL,
        description  TEXT,
        release_year INT,
        rating       REAL
    );
    """)


@app.route("/movie/<int:id>", methods=["GET"])
def movie():
    create_movies_database(db)

    raise NotImplemented

    movies = db.execute(
        """
        SELECT *
          FROM movies        
        """,
    )
