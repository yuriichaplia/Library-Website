from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

class Base(DeclarativeBase):
  pass

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
database = SQLAlchemy(model_class=Base)
database.init_app(app)

class Books(database.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

with app.app_context():
    database.create_all()

@app.route('/')
def home():
    result = database.session.execute(database.select(Books).order_by(Books.title)).scalars().all()
    return render_template('index.html', books=result, book_count=len(result))

@app.route("/add_element", methods=["GET", "POST"])
def add_element():
    if request.method == "POST":
        title = request.form['title']
        author = request.form['author']
        try:
            rating = float(request.form['rating'])
        except ValueError:
            rating = 0.0

        book = Books(title=title, author=author, rating=rating)
        database.session.add(book)
        database.session.commit()

        return redirect(url_for('home'))
    else:
        return render_template('add.html')

@app.route('/edit', methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        book_id = request.form['id']
        book_to_update = database.get_or_404(Books, book_id)
        try:
            book_to_update.rating = float(request.form['new_rating'])
        except ValueError:
            book_to_update.rating = 0.0
        database.session.commit()
        return redirect(url_for('home'))
    book_id = request.args.get('id')
    book_selected = database.get_or_404(Books, book_id)
    return render_template('edit.html', book_selected=book_selected)

@app.route('/delete/<id>')
def delete(id):
    book = database.get_or_404(Books, id)
    database.session.delete(book)
    database.session.commit()

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)