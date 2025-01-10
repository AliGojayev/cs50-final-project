from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import login_required

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


def create_users_database(db: SQL):
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
        username        TEXT    NOT NULL UNIQUE,
        hashed_password TEXT    NOT NULL,
        watched_films   TEXT    DEFAULT NULL
    );
    """)


@app.route("/")
def index():
    # TODO: Create separate index page
    return redirect("/movies")


@app.route("/movies/", methods=["GET", "POST"])
def movies():
    if request.method == "GET":
        return render_template("movies.html")

    if request.method == "POST":
        title = request.form.get("title")

        if not title:
            flash("Must provide the title of the movie", "error")
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


@app.route("/movie/<int:movie_id>", methods=["GET"])
def movie(movie_id):
    # Find movie with provided ID
    try:
        movie = db.execute(
            """
            SELECT *
              FROM movies
             WHERE id = ?;
            """,
            movie_id,
        )[0]
    except IndexError:
        flash("Movie with specified ID was not found", "error")
        return redirect("/movies")

    if movie:
        return render_template("movie.html", movie=movie)
    else:
        flash("Movie with specified ID was not found", "error")
        return redirect("/movies")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Must provide username", "error")
            return redirect("/register")
        elif not password:
            flash("Must provide password", "error")
            return redirect("/register")
        elif not confirmation:
            flash("Must verify your password", "error")
            return redirect("/register")

        # Strip trailing and leading whitespace from credentials
        username = username.strip()
        password = password.strip()
        confirmation = confirmation.strip()

        # If username and password are empty after strip, they were full whitespace
        if not (username and password):
            flash("Blank data in username and password are not allowed", "error")
            return redirect("/register")

        if request.form.get("password") != request.form.get("confirmation"):
            flash("Passwords must be identical", "error")
            return redirect("/register")

        registered_with_same_name = db.execute(
            "SELECT username FROM users WHERE username = ?", username
        )
        if registered_with_same_name:
            flash("Username already taken, choose another one", "error")
            return redirect("/register")

        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        rows = db.execute("SELECT id FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]

        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Must provide username", "error")
            return redirect("/login")

        elif not password:
            flash("Must provide password", "error")
            return redirect("/login")

        # Strip trailing and leading whitespace from credentials
        username = username.strip()
        password = password.strip()

        # If username and password are empty after strip, they were full whitespace
        if not (username and password):
            flash("Blank data in username and password are not allowed", "error")
            return redirect("/register")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username and/or password", "error")
            return redirect("/login")

        session["user_id"] = rows[0]["id"]

        return redirect("/")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")
