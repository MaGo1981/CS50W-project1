CREATE TABLE books
(
  id integer NOT NULL DEFAULT
  isbn character varying NOT NULL,
  title character varying NOT NULL,
  author character varying NOT NULL,
  pub_year character varying NOT NULL,
  CONSTRAINT books_pkey PRIMARY KEY (id)
)