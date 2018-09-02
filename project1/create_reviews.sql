CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    rating INTEGER NOT NULL,
    review VARCHAR NOT NULL,
    recommend_to VARCHAR NOT NULL,
    genre VARCHAR NOT NULL,
    book_id INTEGER REFERENCES books,
    user_id INTEGER REFERENCES users
);