from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os

app = Flask(__name__)

# Set up SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Flask Bieb API)"}
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Initialize the database
db = SQLAlchemy(app)

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/api/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    books_list = [{'id': book.id, 'title': book.title, 'author': book.author} for book in books]
    return jsonify(books_list)

@app.route('/bieb')
def library():
    books = Book.query.all()
    return render_template('bieb.html', books=books)

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')

    if not title or not author:
        return "Missing title or author", 400

    new_book = Book(title=title, author=author)
    db.session.add(new_book)
    db.session.commit()

    return redirect(url_for('bieb'))

@app.route('/api/books', methods=['POST'])
def api_add_book():
    data = request.json
    title = data.get('title')
    author = data.get('author')

    if not title or not author:
        return jsonify({"error": "Missing title or author"}), 400

    new_book = Book(title=title, author=author)
    db.session.add(new_book)
    db.session.commit()

    return jsonify({"message": "Book added", "book": {'title': title, 'author': author}}), 201

if __name__ == '__main__':
    app.run(debug=True)
