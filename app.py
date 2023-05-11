from sqlalchemy import or_
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from datetime import datetime
import phonenumbers, sys

# Import for Migrations
# from flask_migrate import Migrate
import re
from sqlalchemy.orm.attributes import get_history
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://pythontest_user:5qCFcvnYqljdujZ8hUSe7h9C5ztQP5VR@dpg-ch8h6flgk4q7lmqelp10-a.oregon-postgres.render.com/pythontest'
app.secret_key="secret key"
db = SQLAlchemy(app)
# Settings for migrations
# migrate = Migrate(app, db)

def validemail(email):
    regexEmail = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'  
    return True if re.fullmatch(regexEmail,email) else False

def validphone(phone):
    regexPhone = r"(0|91)?[6-9][0-9]{9}"
    return True if re.fullmatch(regexPhone,phone) else False


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone

@db.event.listens_for(Contact, 'after_insert')
def before_contact_insert(mapper, connection, target):
    version = ContactVersion(contact_id=target.id,
                             name=target.name,
                             email=target.email,
                             phone=target.phone,
                             operation='insert')
    db.session.add(version)

@db.event.listens_for(Contact, 'after_update')
def before_contact_update(mapper, connection, target):
    print(target.id)
    old_contact = Contact.query.get(target.id)
    changes = {}
    for attr in ['name', 'email', 'phone']:
        history = get_history(target, attr)
        if history.has_changes():
            changes[attr] = history.deleted[0]
    try: 
        if changes:
            version = ContactVersion(contact_id=target.id,
                                    name=old_contact.name,
                                    email=old_contact.email,
                                    phone=old_contact.phone,
                                    operation='update',
                                    changes=changes)
            db.session.add(version)

    except Exception as e:
        print(e,"in event listener")

@db.event.listens_for(Contact, 'after_delete')
def before_contact_delete(mapper, connection, target):
    version = ContactVersion(contact_id=target.id,
                             name=target.name,
                             email=target.email,
                             phone=target.phone,
                             operation='delete')
    db.session.add(version)

class ContactVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    operation = db.Column(db.String(10), nullable=False)
    changes = db.Column(db.JSON)

    def __init__(self, contact_id, name, email, phone, operation, changes=None):
        self.contact_id = contact_id
        self.name = name
        self.email = email
        self.phone = phone
        self.operation = operation
        self.changes = changes

@app.route('/',methods=['POST','GET'])
def index():
    all_contacts=Contact.query.all()
    if request.method=='POST' and 'tag' in request.form:
        tag=request.form['tag']
        search="{}%".format(tag)
        search_contact=Contact.query.filter(or_(Contact.name.like(search),Contact.email.like(search)))
        return render_template('index.html',contact=search_contact)
    else:
        return render_template('index.html',contact=all_contacts)

@app.route('/insert',methods=['POST'])
def insert():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        phone=request.form['phone']
        try:
            if not validemail(email):
                flash('Enter valid email address!')
                return redirect(url_for('index'))
            elif not validphone(phone):
                flash('Enter valid phone number!')
                return redirect(url_for('index'))
            else:
                my_contact=Contact(name,email,phone)
                db.session.add(my_contact)
                db.session.commit()
                flash('Contact Added Successfully!')
                return redirect(url_for('index'))
        except:
            return 'There was an issue adding your contact!'
    return redirect(url_for('index'))

@app.route('/update', methods=['GET','POST'])
def update():
    if request.method == 'POST':
        my_contact=Contact.query.get_or_404(request.form.get('id'))
        my_contact.name=request.form['name']
        my_contact.email=request.form['email']
        my_contact.phone=request.form['phone']
        try:
            if not validemail:
                flash('Enter valid email address!')
                return redirect(url_for('index'))
            elif not validphone:
                flash('Enter valid phone number!')
                return redirect(url_for('index'))
            else:
                db.session.commit()
                flash('Contact Updated Successfully!')
                return redirect(url_for('index'))
        except:
            return 'There was an issue updating your contact!'
    return redirect(url_for('index'))

@app.route('/delete/<id>', methods=['GET','POST'])
def delete(id):
    my_contact=Contact.query.get_or_404(id)
    try:
        db.session.delete(my_contact)
        db.session.commit()
        flash('Contact Deleted Successfully!')
        return redirect(url_for('index'))
    except:
        return 'There was a problem deleting that contact!'

# versions = ContactVersion.query.filter_by(contact_id=C.id).all()


with app.app_context():
    db.create_all()

if __name__=="__main__":
     app.run(debug=True)