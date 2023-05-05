from flask import Flask, render_template, request, redirect, url_for
import re

app = Flask(__name__)

contacts = [
    {
        'name': 'John Doe',
        'phone': '555-5555',
        'email': 'john.doe@example.com'
    },
    {
        'name': 'Jane Smith',
        'phone': '555-1234',
        'email': 'jane.smith@example.com'
    }
]

@app.route('/')
def home():
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
            contacts.append({'name': name, 'phone': phone, 'email': email})
            return redirect(url_for('home'))
        else:
            return render_template('add_contact.html', error=error)
    else:
        return render_template('add_contact.html')

@app.route('/edit_contact/<int:index>', methods=['GET', 'POST'])
def edit_contact(index):
    contact = contacts[index]
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
            contacts[index] = {'name': name, 'phone': phone, 'email': email}
            return redirect(url_for('home'))
        else:
            return render_template('edit_contact.html', contact=contact, error=error)
    else:
        return render_template('edit_contact.html', contact=contact)

@app.route('/delete_contact/<int:index>')
def delete_contact(index):
    del contacts[index]
    return redirect(url_for('home'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        filtered_contacts = [contact for contact in contacts if query in contact['name'] or query in contact['email']]
        return render_template('search.html', contacts=filtered_contacts, query=query)
    else:
        return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
