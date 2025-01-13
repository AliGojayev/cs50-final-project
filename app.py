from os import path

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import (
    get_table_columns,
    login_required,
    setup_database,
    snake_to_sentence_case,
)

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DATABASE_PATH = "database.db"

# If database file is not created, create it and necessary tables using sqlite
if not path.exists(DATABASE_PATH):
    setup_database(DATABASE_PATH)

db = SQL(f"sqlite:///{DATABASE_PATH}")

# Filter to change snake case of the database column name to sentence case
app.jinja_env.filters["snake_to_sentence_case"] = snake_to_sentence_case


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    criterias = get_table_columns(
        db, "movies", ["id", "genre", "mood", "description", "image_path"]
    )

    if request.method == "POST":
        sort_criteria = request.form.get("sort-criteria")
        sort_order = request.form.get("sort-order")

        if sort_criteria not in criterias:
            flash("Invalid sort criteria", "error")
            return redirect("/")

        if sort_order not in ("ASC", "DESC"):
            flash("Invalid sort order", "error")
            sort_order = "ASC"
    else:
        sort_criteria = "title"
        sort_order = "ASC"

    user_id = session["user_id"]

    all_movies = db.execute(
        f"SELECT id, title, release_year FROM movies ORDER BY {sort_criteria} {sort_order};"
    )

    # TODO: Optimize query
    watched_movie_ids = [
        movie["id"]
        for movie in db.execute(
            """
            SELECT m.id
              FROM movies m
              JOIN watched_movies wm ON m.id = wm.movie_id
             WHERE wm.user_id = ?
            """,
            user_id,
        )
    ]

    return render_template(
        "index.html",
        criterias=criterias,
        all_movies=all_movies,
        watched_movie_ids=watched_movie_ids,
    )


@app.route("/watched", methods=["GET"])
@login_required
def watched_movies():
    user_id = session["user_id"]

    watched_movies = db.execute(
        """
        SELECT m.id, m.title, m.release_year, wm.rating
          FROM movies m
          JOIN watched_movies wm ON m.id = wm.movie_id
         WHERE wm.user_id = ?;
        """,
        user_id,
    )

    return render_template("watched_movies.html", watched_movies=watched_movies)


@app.route("/mark-watched", methods=["POST"])
@login_required
def mark_watched():
    user_id = session["user_id"]
    movie_id = request.form.get("movie_id")

    if movie_id:
        try:
            db.execute(
                """
                INSERT INTO watched_movies (user_id, movie_id)
                VALUES (?, ?)
                ON CONFLICT (user_id, movie_id) DO NOTHING;
                """,
                user_id,
                movie_id,
            )
            flash("Movie marked as watched", "success")
        except Exception as e:
            flash("Error marking movie as watched", "error")
            print(e)

    return redirect("/watched")


@app.route("/mark-unwatched", methods=["POST"])
@login_required
def mark_unwatched():
    user_id = session["user_id"]
    movie_id = request.form.get("movie_id")

    if movie_id:
        try:
            db.execute(
                "DELETE FROM watched_movies WHERE user_id = ? AND movie_id = ?;",
                user_id,
                movie_id,
            )
            flash("Movie marked as unwatched", "success")
        except Exception as e:
            flash("Error marking movie as watched", "error")
            print(e)

    return redirect("/")


@app.route("/rate-movie", methods=["POST"])
@login_required
def rate_movie():
    user_id = session["user_id"]
    movie_id = request.form.get("movie_id")
    rating = request.form.get("rating")

    if movie_id and rating:
        try:
            if rating == "remove-rating":
                rating = None
            else:
                rating = int(rating)

            if not rating or (1 <= rating <= 10):
                db.execute(
                    """
                    UPDATE watched_movies
                       SET rating = ?
                     WHERE user_id = ? AND movie_id = ?;
                    """,
                    rating,
                    user_id,
                    movie_id,
                )
                if rating:
                    flash(f"Movie rated successfully with ★{rating}!", "success")
                else:
                    flash("Successfully removed rating from the movie!", "success")
            else:
                flash("Rating must be between 1 and 10", "error")
        except ValueError:
            flash("Invalid rating", "error")
        except Exception as e:
            flash("Error rating movie", "error")
            print(e)

    return redirect("/watched")


@app.route("/movies/", methods=["GET", "POST"])
def movies():
    criterias = get_table_columns(db, "movies", ["id", "image_path"])

    if request.method == "GET":
        return render_template("movies.html", criterias=criterias)

    if request.method == "POST":
        search_criteria = request.form.get("search-criteria")
        search_query = request.form.get("search-query")

        if not search_criteria:
            flash("Must provide movie search criteria", "error")
            return render_template("movies.html", criterias=criterias)

        if not search_query:
            flash(f"Must provide the {search_criteria} of the movie", "error")
            return render_template("movies.html", criterias=criterias)

        if search_criteria not in criterias:
            flash("Provided search criteria is not correct", "error")
            return render_template("movies.html", criterias=criterias)

        movies = db.execute(
            f"""
            SELECT *
              FROM movies
             WHERE {search_criteria} LIKE ?;
            """,  # SQL Injection is not possible as `search_criteria` variable is checked beforehand
            "%" + search_query + "%",
        )

        if not movies:
            flash("Movie not found", "error")
            return render_template("movies.html", criterias=criterias)

        return render_template("movies.html", criterias=criterias, movies=movies)


@app.route("/movie/<int:movie_id>", methods=["GET"])
def movie(movie_id):
    # Find movie with provided ID
    try:
        movie = db.execute(
            "SELECT * FROM movies WHERE id = ?;",
            movie_id,
        )[0]
    except IndexError:
        flash("Movie with specified ID was not found", "error")
        return redirect("/movies")

    if not movie:
        flash("Movie with specified ID was not found", "error")
        return redirect("/movies")

    user_id = session.get("user_id")
    # Try to find the value of the user rating
    user_rating = db.execute(
        "SELECT rating FROM watched_movies WHERE user_id = ? AND movie_id = ?;",
        user_id,
        movie["id"],
    )

    # If user rating was found, unwrap it from the list and dictionary
    if user_rating:
        user_rating = user_rating[0]["rating"]

    return render_template("movie.html", movie=movie, user_rating=user_rating)


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


@app.route("/add_movie", methods=["GET", "POST"])
def add_movie():
    if request.method == "GET":
        return render_template("add_movie.html")

    if request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year")
        genre = request.form.get("genre")
        rating = request.form.get("rating")
        mood = request.form.get("mood")
        description = request.form.get("description")

        if not title:
            flash("Must provide movie title", "error")
            return redirect("/add_movie")

        if not year:
            flash("Must provide movie year", "error")
            return redirect("/add_movie")

        if not mood:
            flash("Must provide movie mood", "error")
            return redirect("/add_movie")

        if not description:
            flash("Must provide movie description", "error")
            return redirect("/add_movie")

        if not genre:
            flash("Must provide movie genre", "error")
            return redirect("/add_movie")

        if not rating:
            flash("Must provide movie rating", "error")
            return redirect("/add_movie")

        try:
            year = int(year)
        except ValueError:
            flash("Year must be a number", "error")
            return redirect("/add_movie")

        try:
            rating = int(rating)
            if not 1 <= rating <= 10:
                flash("Rating must be between 1 and 10", "error")
                return redirect("/add_movie")
        except ValueError:
            flash("Rating must be a number", "error")
            return redirect("/add_movie")

        db.execute(
            """
            INSERT INTO movies (title, release_year, mood, genre, rating)
            VALUES (?, ?, ?, ?, ?);
            """,
            title,
            year,
            mood,
            genre,
            rating,
            description,
        )

        flash("Movie added successfully", "success")

        return redirect("/add_movie")
