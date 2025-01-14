# FilmTrckr

Flask application that makes managing your movie tracking easier.

## What is it?

FilmTrckr is a Flask application that allows users to find movies they may enjoy and rate them. It can be used with and without an account.

## How it is different from IMDb?

IMDb and other similar sites are unnecessary complex and require beforehand preparations to recommend you movies.
Moreover, they [track and collect your personal information for advertisement purposes](https://tosdr.org/enservice/313).
Our application does not track users, does not require anything except username and password for account creation, and is as easy to self-host [as any other Flask application](https://flask.palletsprojects.com/en/stable/deploying).

## Used technologies

FilmTrckr exists thanks to these projects:

- [Flask](https://flask.palletsprojects.com/) - micro web framework for Python
- [SQLite](https://sqlite.org/about.html) - lightweight database library written in C
- [Jinja](https://jinja.palletsprojects.com/en/stable/) - templating engine used in Flask
- [Bootstrap](https://getbootstrap.com/) - beautiful and simple front-end framework
- [CS50 Python library](https://cs50.readthedocs.io/libraries/cs50/python/) - database interaction

## Installation

Foremost, install virtual environment.
Virtual environments allow developers to use a clean Python environment for separate projects to prevent [dependency hell](https://en.wikipedia.org/wiki/Dependency_hell) across programs.
On Debian Linux, Ubuntu and its derivatives run:

```shell
sudo apt install python3-pip
sudo apt install virtualenv

python3 -m venv .venv
source .venv/bin/activate
```

Then install all required dependencies:

```shell
pip install -r requirements.txt
```

### Using with sample database

If you want to just test application or start with something other than "blank canvas", you can use application with preloaded sample data (used from IMDb).

### Using just application with no sample data

If you want to add all movies on your own, you delete sample data from application:

```shell
find ./static/ ! -name '_not-found.jpg' -type f -exec rm -f {} +
rm database.db
```

Don't worry about the database file, it will be created will all required tables on the next Flask application startup.

### Running Flask application

For development (non-production) purposes, FilmTrckr can be started with a `flask run` command.
If required, additional `-debug` flag can be passed to [show error and exception messages directly in the browser](https://flask.palletsprojects.com/en/stable/quickstart/#debug-mode).

After that, you access your application on 127.0.0.1:5000 or localhost:5000 by our web browser.

## Usage

FilmTrckr has these pages:
- `/` (index, requires and account)
- `/watched` (index of watched movies, requires an account)
- `/movies` (movie search page)
- `/movie` (detailed movie info page)
- `/add_movie` (movie insertion page, requires an account)
- `/register` (account registration form)
- `/login` (sign in form)

### app.py

Is the main part of this program where all the functions are called abd executed.
Here is written the logic for pages index, watched, movies, movie, add_movie, register, login, which I will explain in details further.

### layout
The `layout.html` file provides the foundational structure and styling for the entire website, creating a consistent layout for each page that extends this base template.

- Head Section
    - Meta Tags: The charset is set to UTF-8, and the viewport is configured for responsive design.
    - Title: The title is set to "FilmTrackr" by default, but it can be customized by child templates using the {% block title %} tag.
    - CSS: The page uses Bootstrap 5 for responsive design and custom styles. The custom CSS modifies the body’s background color, text color, and the appearance of the navigation bar and flashed messages.
    - Navbar
        - The navigation bar features a dark background and yellow accents (#f5c518).
        - Brand: The brand "FilmTrackr" is highlighted with bold text and a yellow color.
        - Menu Items:
            - If the user is logged in (i.e., `session["user_id"]` is set), the navbar displays links to pages like "Movie Tracker," "Watched," "Search Movies," and "Add Movie."
            - If the user is not logged in, the navbar shows options to register or log in, along with a link to search movies.
            - The navbar adapts to different screen sizes, collapsing into a toggleable menu on smaller screens.
    - Flashed Messages
        - The flashed messages system is used to display feedback to the user.
        - Error and Success Messages: Different message categories (like error and success) are shown with distinct styles (red for errors and green for successes).
        - These messages are placed in a container and use Bootstrap alerts for a responsive, dismissible UI.
- Body Content
    - The `{% block body %}` placeholder is where child templates can insert their specific content. This ensures that the body of each page is unique while maintaining a consistent overall structure.
- Footer
    - The footer has a simple design with a dark background (#1a1a1a) and light text (#bbb), ensuring it is subtle yet visible.
- User Experience
    - The layout ensures a consistent design across the entire website, making it easy to navigate and interact with. The use of Bootstrap ensures the page is responsive and adjusts to different screen sizes.

### Index

The index page displays all movies and requires a user login.
It highlights unwatched movies with a Not watched yet badge and provides a Mark as Watched button for quick updates.
Users can sort movies by criteria (e.g., title, genre) and order (ascending or descending).
Criteria options are generated from the `criterias` variable and displayed in sentence case using the `snake_to_sentence_case` filter.
A submit button triggers a POST request to sort the movies.

### Movie List

Movies are listed with their titles and release years.
Titles link to detailed pages (`/movie/{{ movie.id }}`).
A badge and `Mark as Watched` button are shown for unwatched movies.
The button sends a POST request to `/mark-watched` with the movie ID.

Bootstrap components ensure responsive layout and intuitive interaction.
Users can efficiently track watched movies and customize the displayed order.

### Watched

The watched movies page displays a personalized list of movies that a logged-in user has marked as watched.

Movie List
Each movie entry shows the title, release year, and user-assigned rating (if available).
Titles link to detailed pages (`/movie/{{ movie.id }}`).
A Rate button allows users to assign or update a rating from 1 to 10, while a Remove Rating option clears the rating.
A Mark as Unwatched button sends a POST request to `/mark-unwatched` with the movie ID to update the watched status.

Bootstrap styles provide a clear, mobile-friendly layout.
Users can manage ratings and watched status with minimal effort.

### Movies

The movies page provides a search interface for users(even without the account) to explore and filter movies by different criteria.

Search Form
Users enter a query in a text input and choose a search criterion from a dropdown menu (e.g., title, genre, mood).
Criteria options are dynamically generated from the `criterias` variable and displayed in sentence case using the `snake_to_sentence_case` filter.
A Search button sends a POST request to `/movies` with the query and selected criterion.

If movies matching the search are found, a table displays:
    - Title (linked to the detailed movie page `/movie/{{ movie.id }}`)
    - Genre, Mood, Year, and Rating
Each row represents a movie with its key attributes for easy identification.

If not the it flashes error.

Bootstrap components create a structured and responsive layout.
Table-based results ensure clear and accessible data presentation.

### Movie

Movie Information
    - Title: Displayed prominently as a header in large, bold text.
    - Attributes Table: A table shows the movie's key details:
    - Genre, Mood, Year, and Rating.

A responsive image is shown on the left side, linked from the static directory using url_for.
A brief description is presented beside the image, providing insights into the movie's content.

A dark, cinema-like theme using a black background and white/light grey text for contrast.
Custom styles (movie-title, movie-description) enhance readability and design consistency.
The card layout with a shadow effect creates a modern, elevated display.

A Back to Movies button allows users to return to the main movies list for further exploration.

### Add movie

The `add_movie.html` template allows users to add a new movie to the platform, providing a form to submit movie details.

A custom yellow button is created using the `.btn-yellow` class, which matches the brand's color scheme. On hover, the button color changes to a darker shade (#d4a017) to provide visual feedback.

Page Structure
    - Title: The page title is set to "Add Movie," and this can be customized further by child templates using `{% block title %}`.
    - Main Content: The form provides fields for movie details, including:
    - Movie Title: A text input for the movie's name.
    - Release Year: A number input for the year of release, with validation to ensure it's a valid number.
    - Genre: A text input for the genre of the movie.
    - Rating: A number input for rating the movie on a scale from 1 to 10, with validation to ensure the rating is within the allowed range.
    - Mood: A text input for describing the mood of the movie.
    - Description: A larger text area for the movie description, allowing users to add additional context about the movie.

Each input field has associated validation messages, which will be displayed if the user tries to submit the form without filling out the required fields correctly.
These messages provide feedback such as "Please provide a movie title" or "Please provide a valid year."

The form submits via the POST method to `/add_movie`, which triggers the backend process to store the movie information.
The submit button has the custom `.btn-yellow` class for consistent styling with the rest of the site.

By using this template, users can easily add new movies to the platform while maintaining a consistent and user-friendly interface.

### Register

To use some pages, a user will need to have an account.
Username, password and its confirmation will be asked to create an account.
Password are stored hashed using scrypt hash algorithm (hashing [is handled](https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security) by werkzeug library).
The python code detects all errors and flashes inform users about them.
Note that username and password created with whitespace characters only (spaces, tabs and so on) are not allowed.

### login

The `login.html` template provides a login form for users.

Input fields for the username and password, with the username field set to autofocus and no autocomplete.
Form submits POST request to `/login` for authentication.

A full-width Log In button styled with `btn-dark`.

The python code detects all errors and flashes inform users about them.

The page uses a responsive layout with a card for a clean, modern appearance, ensuring easy access for users to log in.

## Database overview

To handle all application functionality, FilmTrckr uses 3 tables in SQLite databases.

- `movies`
    - Stores all required information for each individual movie.
    - All fields are necessary (`NOT NULL`).
- `users`
    - Stores username and hashed password.
- `watched_movies`
    - Stores information about what who watched what movie and user-set ratings.
    - All fields except rating must be set to some value (NOT NULL).
    - `user_id` and `movie_id` are foreign keys to `id` fields of `user` and `movie` tables, respectively.

## Separation of duties

The work with front-end of the program was almost completely on Ali Gojayev
Initiating the repository, the code and the program itself was made by Said Gulmetov
Such functions as index(),watched_movies(),movies(),movie(movie_id),register(),login(),logout() were made by Said Gulmetov
The remaining functions were made by Ali Gojayev
The work with the databases was completely on Said Gulmetov```
