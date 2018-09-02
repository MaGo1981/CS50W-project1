import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, pub_year in reader:
        db.execute("INSERT INTO books (isbn, title, author, pub_year) VALUES (:isbn, :title, :author, :pub_year)",
                    {"isbn": isbn, "title": title, "author": author, "pub_year":pub_year})
        print(f"Added books isbn: {isbn}, title: {title}, author: {author}, year: {pub_year}  to books table.")
    db.commit()

if __name__ == "__main__":
    main()
