from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

# To make this into something i would actually use, it needs a search function and key word tag.

app = Flask(__name__)

## Create the Book Database
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"

# Create the extension
db = SQLAlchemy(model_class=Base)
# Initialise the app with the extension
db.init_app(app)


##CREATE TABLE
class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str]  = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()

## HOME PAGE
@app.route('/')
def home():
    # READ ALL DB RECORDS
    all_records = db.session.execute(db.select(Book).order_by(Book.title))
    all_books = all_records.scalars()
    return render_template("index.html",display_books=all_books)

## ADD A NEW BOOK
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method== "POST":
        #Create a record
        new_book = Book(
            title = request.form["title"],
            author = request.form["author"],
            description = request.form["description"],
            rating = request.form["rating"],
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("home"))
    else:
        return render_template("add.html")


# EDIT A BOOKS RATING
@app.route("/edit_rating", methods=["GET", "POST"])
def edit_rating():
    if request.method== "POST":
        #Update record
        book_id = request.form["id"]
        new_rating = request.form["new_rating"]
        # Go find the record
        book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        #Update the record
        book_to_update.rating = new_rating
        db.session.commit()  
        return redirect(url_for("home"))
    else:
        book_id = request.args.get("id")
        book_selected = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        return render_template("edit_rating.html", book = book_selected)


@app.route("/delete_book")
def delete_book():
    # Book to delete
    book_id = request.args.get("id")
    book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()

    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


## Turns debug on
if __name__ == "__main__":
    app.run(debug=True)

