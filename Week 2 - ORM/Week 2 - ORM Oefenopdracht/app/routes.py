import math, sqlite3
from flask import render_template, redirect, url_for, flash, request
import sqlalchemy as sa
from app import app, db
from app.models import User
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/') 
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def inloggen():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return render_template('login.html', form=form)
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('inloggen'))
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
    c.execute('INSERT INTO phonebook (naam, telefoonnummer, adres, woonplaats) VALUES (?, ?, ?, ?)', 
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
    c.execute('UPDATE phonebook SET naam = ?, telefoonnummer = ?, adres = ?, woonplaats = ? WHERE id = ?', 
              (name, phone_number, adres, stad, id))
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