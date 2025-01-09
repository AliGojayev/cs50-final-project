from cs50 import SQL
from flask import (
    Flask,
    flash,
    render_template,
    request,
)

from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///database.db")


# TODO: Execute once before server start
def create_movies_database(db: SQL):
    db.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        title        TEXT    NOT NULL,
        genre        TEXT    NOT NULL,
        mood         TEXT    NOT NULL,
        description  TEXT,
        release_year INTEGER,
        rating       REAL
    );
    """)


@app.route("/movies/", methods=["GET", "POST"])
def movies():
    if request.method == "GET":
        return render_template("movies.html")

    title = request.form.get("title")

    if not title:
        return render_template("movies.html")

    movies = db.execute(
        """
        SELECT *
          FROM movies
         WHERE title LIKE ?;
        """,
        "%" + title + "%",
    )

    if not movies:
        flash("Movie not found", "error")
        return render_template("movies.html")

    return render_template("movies.html", movies=movies)
