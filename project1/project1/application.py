import os

from flask import Flask, session,render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")



@app.route("/register", methods=["GET","POST"])
def register():
	name = request.form.get("name")
	email = request.form.get("email")
	passw = request.form.get("passw")
	if request.method == 'POST':
		db.execute("INSERT INTO users(name, email, passw) VALUES (:name, :email, :passw)",
			{"name": name, "email": email, "passw": passw})
		db.commit()
		return redirect(url_for('login'))
	return render_template("register.html")




@app.route("/login", methods=["GET","POST"])
def login():
	session["name"] = request.form.get("username")
	session["logged_in"]=True
	session["user_id"]= db.execute("SELECT id FROM users WHERE name='user3'").fetchone()
	return render_template("login.html", user_id=session["user_id"])





@app.route("/main", methods=["GET","POST"])
def main():
	username=request.form.get("username")
	return render_template("main.html", username=username)

@app.route("/logout", methods=["GET","POST"])
def logout():
	return render_template("index.html")



@app.route("/books")
def books():
    """Lists all books."""
    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("books.html", books=books)


@app.route("/books/<int:book_id>")
def book(book_id):
    """Lists details about a single book."""

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")
    return render_template("book.html", book=book)




@app.route("/users", methods=["GET","POST"])
def users():
	# List users
	try:
		session["users"] = db.execute("SELECT name FROM users").fetchall()
		print("\nUsers:")
		for user in session["users"]:
			print(user.name)
		return render_template("users.html", users=session["users"])
	except:
		session["users"]=["Marko", "Marina"]
		return render_template("users.html", users=session["users"])



@app.route("/home", methods=["GET","POST"])
def register1():
    # imena unosa 'name', 'email', 'pass' po poljima forms (FLASK - forms)
    name = request.form.get("name1")
    email = request.form.get("email1")
    passw = request.form.get("passw1")
    if request.method == 'POST':
	    db.execute("INSERT INTO users(name, email, passw) VALUES (:name, :email, :passw)",
	                {"name": name, "email": email, "passw": passw})
	    db.commit()

	    return redirect(url_for('register1'))
    return render_template("home.html")

@app.route("/home", methods=["GET","POST"])
def login1():
	name = request.form.get("name2")
	passw = request.form.get("passw2")
	db_passw = db.execute("SELECT users.passw FROM users WHERE name = name").fetchone()
	if request.method == 'POST':
		if db_passw == passw:
			return redirect(url_for('login'))
	return render_template("home.html")
