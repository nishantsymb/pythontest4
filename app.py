from flask import Flask, render_template, request, redirect, url_for
import re
import psycopg2
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

conn = psycopg2.connect(
    dbname="flask_contacts",
    user="flaskuser",
    password="password",
    host="localhost",
    port="5432"
)

@app.route('/')
def home():
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts;")
    contacts = cur.fetchall()
    cur.close()
    return render_template('home.html', contacts=contacts)

@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        error = None
        if not name:
            error = 'Name is required.'
        elif not phone:
            error = 'Phone number is required.'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            error = 'Invalid email address.'
        if error is None:
            cur = conn.cursor()
            cur.execute("INSERT INTO contacts (name, phone, email) VALUES (%s, %s, %s);", (name, phone, email))
            conn.commit()
            cur.close()
            return redirect(url_for('home'))
        else:
            return render_template('add_contact.html', error=error)
    else:
        return render_template('add_contact.html')

@app.route('/edit_contact/<int:index>', methods=['GET', 'POST'])
def edit_contact(index):
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts WHERE id = %s;", (index,))
    contact = cur.fetchone()
    cur.close()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        error = None
        if not name:
            error = 'Name is required.'
        elif not phone:
            error = 'Phone number is required.'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            error = 'Invalid email'
