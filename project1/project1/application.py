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
		db_user_id = db.execute("SELECT id FROM users WHERE name = :name",
                             {"name": session["name"]}).fetchone()
		db_names = db.execute("SELECT name FROM users").fetchall()
		# print (session['name'])
		# print(session['password'])
		# print(db_name[0])
		# print(db_password[0])
		# print(db_user_id[0])
		# user_list=[]
		# n=0
		# for ime in db_names:
			# print(db_names[n][0])
			# user_list.append(db_names[n][0])
			# n=n+1
		# print (user_list)

		# if session['name'] not in user_list:
		# 	message = "Username unknown, please try again!"
		# 	session['name']= None
		# 	return render_template("error.html", message=message)

		if db_name is None or \
		session['name'] != db_name[0]  or \
		session['password'] != db_password[0]:
			message = "Wrong username or password, please try again!"
			session['name']= None
			return render_template("error.html", message=message)
		else:
			session['logged_in'] = True
			session['name']= db_name[0]
			session['user_id']= db_user_id[0]
			return redirect(url_for('main'))
	return render_template("login.html")






@app.route("/main", methods=["GET","POST"]) #/<string:username> ili /<string:search> Dynamic Routes RP2 pg 44
@login_required
def main():
	if request.method == 'POST':
		try:
			bookSearch=request.form.get("searchform")
			bookSearch='%'+bookSearch+'%'
			if bookSearch == '%%':
				return render_template("main.html")
			else:
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


	# Get data from input form	
	rating = int(4)
	review = request.form.get("review")
	recommend_to = request.form.get("recomend")
	genre = "action novel"
	user_id=session['user_id']


	# List reviews
	reviews = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book_id}).fetchall()

	# Select data from two different tables
	db_info = db.execute("SELECT name, rating, recommend_to, genre, review, book_id FROM users JOIN reviews ON reviews.user_id = users.id WHERE reviews.user_id = users.id and book_id= :id", {"id": book_id}).fetchall()

	print(db_info)

	# Check if user already submitted a review for the book, if not - submit
	db_user_check = db.execute("SELECT user_id FROM reviews WHERE user_id = :user_id", {"user_id": user_id}).fetchone()
	db_book_id_check = db.execute("SELECT book_id FROM reviews WHERE user_id = :user_id", {"user_id": user_id}).fetchall() 
	# dobijemo listu tople elemenata koji sadrže book id za koji je ovaj korisnik predao review (dvaput za 117) - [(4843,), (117,), (592,), (117,)]
	# stvaramo listu brojeva da možemo provjeravati u petlji
	db_book_id_check_list = []

	for tup in db_book_id_check:
		db_book_id_check_list.append(tup[0])


	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "QLHk8LGi3X0XHiqWXA9Jw", "isbns": "1632168146"})
	print(res.json())
	print(res.json()['books'][0]['id']) # izvlacenje pojedinih vrijednosti iz JSON-A
	'''{'books': [{'id': 29207858, 'isbn': '1632168146', 'isbn13': '9781632168146', 'ratings_count': 0, 'reviews_count': 2, 'text_reviews_count': 0, 'work_ratings_count': 26, 'work_reviews_count': 114, 
	'work_text_reviews_count': 10, 'average_rating': '4.04'}]}'''

	if request.method == 'POST':
		if db_user_check is not None and user_id == db_user_check[0]:
			if book_id in db_book_id_check_list:
				message = "You have already submited a review for this book!"
				return render_template("error.html", message=message)
		try:
			db.execute("INSERT INTO reviews(rating, review, recommend_to, genre, book_id, user_id) VALUES (:rating, :review, :recommend_to, :genre, :book_id, :user_id)",
				{"rating": rating, "review": review, "recommend_to": recommend_to, "genre": genre, "book_id": book_id, "user_id": user_id})
			db.commit()
			return render_template("book.html", book=book, reviews=reviews, db_info=db_info)
		except:
			message = "Your review was not excepted. Check your code."
			return render_template("error.html", message=message)
	return render_template("book.html", book=book, reviews=reviews, db_info=db_info)


@app.route("/logout", methods=["GET","POST"])
def logout():
	session.pop('logged_in', None)
	session.pop('name', None)
	session.pop('user_id', None)	
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


@app.route("/home")
def home():
    return render_template("home.html")