import os

from flask import Flask, session,render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests

from functools import wraps


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



def login_required(test):
	@wraps(test)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return test(*args, **kwargs)
		else:
			flash('You need to login first.')
			return redirect(url_for('login'))
	return wrap



@app.route("/")
def index():
    return render_template("index.html")



@app.route("/register", methods=["GET","POST"])
def register():

	if request.method == 'POST':
		name = request.form.get("name")
		email = request.form.get("email")
		passw = request.form.get("passw")
		repeatPass = request.form.get("repeatPass")
		db_name_check = db.execute("SELECT name FROM users WHERE name = :name",
	                             {"name": name}).fetchone()
		# print(db_name_check[0])
		# print(name)

		# not None mora biti jer ne mozes usporedjivati None type varijablu
		if db_name_check is not None and name == db_name_check[0]:
			message = "That user is already taken. Click 'back' and try again!"
			return render_template("error.html", message=message)
		elif passw != repeatPass:
			message = "Your password and repeated password did not match. Click 'back' and try again!"
			return render_template("error.html", message=message)
		else:
			try:
				db.execute("INSERT INTO users(name, email, passw) VALUES (:name, :email, :passw)",
					{"name": name, "email": email, "passw": passw})
				db.commit()
				return redirect(url_for('login'))
			except:
				message = "Your code has crashed!"
				return render_template("error.html", message=message)
	return render_template("register.html")




@app.route("/login", methods=["GET","POST"])
def login():
	if request.method == 'POST':
		session['name'] = request.form.get('username')
		# saved in a browser cookie - not good for password!? but do i have to transfer variable in render template? 
		session['password'] = request.form.get('pass')
		db_name = db.execute("SELECT name FROM users WHERE name = :name",
                             {"name": session["name"]}).fetchone()
		db_password = db.execute("SELECT passw FROM users WHERE name = :name",
                             {"name": session["name"]}).fetchone()
		print (session['name'])
		print(session['password'])
		print(db_name[0])
		print(db_password[0])
		

		if session['name'] != db_name[0]  or \
		session['password'] != db_password[0]:
			message = "Wrong password, please try again!"
			session['name']= None
			return render_template("error.html", message=message)
		else:
			session['logged_in'] = True
			session['name']= db_name[0]
			return redirect(url_for('main'))
	return render_template("login.html")






@app.route("/main", methods=["GET","POST"]) #/<string:username> ili /<string:search> Dynamic Routes RP2 pg 44
@login_required
def main():
	if request.method == 'POST':
		try:
			bookSearch=request.form.get("searchform")
			bookSearch='%'+bookSearch+'%'
			books = db.execute("SELECT * FROM books WHERE isbn LIKE :word  OR title LIKE :word OR author LIKE :word",
								{"word": bookSearch}).fetchall()
			return render_template("main.html", books=books)
		except:
			message = "Your code has crashed! Go back to route /main without logging in!"
			return render_template("error.html", message=message)
	else:
		return render_template("main.html")





@app.route("/books", methods=["GET","POST"])
@login_required
def books():
	"""Lists all books."""
	books = db.execute("SELECT * FROM books").fetchall()
	return render_template("books.html", books=books, name=session["name"])




@app.route("/books/<int:book_id>", methods=["GET","POST"])
@login_required
def book(book_id):
	"""Lists details about a single book."""

	# Make sure book exists.
	book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
	if book is None:
		return render_template("error.html", message="No such book.")

	rating = int(4)
	review1 = request.form.get("review")
	recommend_to = request.form.get("recomend")
	genre = "action novel"
	# List reviews
	reviews = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book_id}).fetchall()

	if request.method == 'POST':
		try:
			db.execute("INSERT INTO reviews(rating, review, recommend_to, genre, book_id) VALUES (:rating, :review, :recommend_to, :genre, :book_id)",
				{"rating": rating, "review": review1, "recommend_to": recommend_to, "genre": genre, "book_id": book_id})
			db.commit()
			return render_template("book.html", book=book, reviews=reviews)
		except:
			message = "Your review was not excepted. Check your code."
			return render_template("error.html", message=message)
	return render_template("book.html", book=book, reviews=reviews)


@app.route("/logout", methods=["GET","POST"])
def logout():
	session.pop('logged_in', None)
	session.pop('name', None)	
	return render_template("login.html")





#--------------------------------------------------------------------------------------------------------



@app.route("/users", methods=["GET","POST"])
def users():
	# List users
	try:
		session["users"] = db.execute("SELECT name, passw FROM users").fetchall()
		print("\nUsers:")
		for user in session["users"]:
			print(user.name)
		return render_template("users.html", users=session["users"])
	except:
		session["users"]=["Marko", "Marina"]
		return render_template("users.html", users=session["users"])
