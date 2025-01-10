from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import login_required, snake_to_sentence_case

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///database.db")

# Filter to change snake case of the database column name to sentence case
app.jinja_env.filters["snake_to_sentence_case"] = snake_to_sentence_case


@app.route("/")
def index():
    # TODO: Create separate index page
    return redirect("/movies")


@app.route("/movies/", methods=["GET", "POST"])
def movies():
    criterias = [
        column["name"]
        for column in db.execute("SELECT name FROM pragma_table_info('movies');")
    ]

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
