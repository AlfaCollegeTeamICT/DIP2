import sqlite3
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
import os
import math

def create_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS login (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    # c.execute('''CREATE TABLE IF NOT EXISTS phonebook (
    #     id INTEGER PRIMARY KEY, 
    #     naam TEXT, 
    #     telefoonnummer TEXT,
    #     adres TEXT,
    #     woonplaats TEXT
    # )''')
    conn.commit()
    conn.close()

create_db()


app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    c.execute('SELECT * FROM login WHERE id = ?', (user_id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2])
    return None

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@app.route('/') 
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def inloggen():
    form = LoginForm()
    if form.validate_on_submit():
        conn = sqlite3.connect("./database.db")
        c = conn.cursor()
        c.execute('SELECT * FROM login WHERE username = ?', (form.username.data,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[2], form.password.data):
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = sqlite3.connect("./database.db")
        c = conn.cursor()
        c.execute('SELECT * FROM login WHERE username = ?', (form.username.data,))
        user = c.fetchone()
        if user is None:
            hashed_password = generate_password_hash(form.password.data)
            c.execute('INSERT INTO login (username, password) VALUES (?, ?)', (form.username.data, hashed_password))
            conn.commit()
            conn.close()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('inloggen'))
        else:
            flash('Username already exists. Please choose a different one.', 'danger')
        conn.close()
    return render_template('register.html', title='Register', form=form)



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/phonebook')
@login_required
def phonebook():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page
    
    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM phonebook')
    total_contacts = c.fetchone()[0]
    
    c.execute('SELECT * FROM phonebook LIMIT ? OFFSET ?', (per_page, offset))
    contacts = c.fetchall()
    
    conn.close()
    
    total_pages = math.ceil(total_contacts / per_page)
    
    return render_template('phonebook.html', contacts=contacts, page=page, total_pages=total_pages)

@app.route('/add_contact', methods=['POST'])
@login_required
def add_contact():
    name = request.form['naam']
    phone_number = request.form['telefoonnummer']
    address = request.form['address']
    city = request.form['city']
    
    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    c.execute('INSERT INTO phonebook (name, phone_number, address, city) VALUES (?, ?, ?, ?,)', 
              (name, phone_number, address, city))
    conn.commit()
    conn.close()
    flash('Contact added successfully', 'success')
    return redirect(url_for('phonebook'))

@app.route('/edit_contact/<int:id>', methods=['POST'])
@login_required
def edit_contact(id):
    name = request.form['naam']
    phone_number = request.form['telefoonnummer']
    adres = request.form['address']
    stad = request.form['woonplaats']
    
    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    c.execute('UPDATE phonebook SET name = ?, phone_number = ?, address = ?, city = ?, WHERE id = ?', 
              (name, phone_number, address, city, id))
    conn.commit()
    conn.close()
    flash('Contact updated successfully', 'success')
    return redirect(url_for('phonebook'))


@app.route('/delete_contact/<int:id>')
@login_required
def delete_contact(id):
    conn = sqlite3.connect("./database.db")
    c = conn.cursor()
    c.execute('DELETE FROM phonebook WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Contact deleted successfully', 'success')
    return redirect(url_for('phonebook'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Oepsie!</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
    </head>
    <body>
        <div class="container text-center mt-5">
            <div class="alert alert-danger" role="alert">
                Je moet ingelogt zijn om dit te kunnen doen.
            </div>
            <a href="/" class="btn btn-primary">Ga terug</a>
        </div>
    </body>
    </html>
    '''

create_db()

if __name__ == '__main__':
    app.run(debug=True)
