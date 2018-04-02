from flask import Flask, render_template, request, redirect, jsonify, url_for,\
    flash
from flask import session as login_session
from flask import make_response
from functools import wraps
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Technology, Machine
import random
import string
import httplib2
import json
import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']
APPLICATION_NAME = '3D Printing Machines App'


# Connect to Database and create database session
engine = create_engine('sqlite:///printingmachines.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Helper functions
def get_user_info(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def create_user(login_session):
    new_user = User(name=login_session['username'],
                    email=login_session['email'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash('You are not allowed to access there')
            return redirect('/login')
    return decorated_function


# Create anti-forgery state token
@app.route('/login')
def get_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Connect to Google Login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
                                            connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    return output


# Disconnect from Google, revoke token, and delete stored user information
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully logged out \
                                from gdisconnect'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token \
                                            for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Log out from Google, then direct to home page
@app.route('/logout')
def disconnect():
    gdisconnect()
    return redirect(url_for('display_technologies'))


# Generate technology and machine information via JSON APIs
@app.route('/technology/JSON')
def technologyJSON():
    technologies = session.query(Technology).all()
    return jsonify(technologies=[r.serialize for r in technologies])


@app.route('/technology/<int:technology_id>/machine/JSON')
def machinesJSON(technology_id):
    technology = session.query(Technology).filter_by(id=technology_id).one()
    machines = session.query(Machine).filter_by(technology_id=technology_id)\
        .all()
    return jsonify(machines=[r.serialize for r in machines])


@app.route('/technology/<int:technology_id>/machine/<int:machine_id>/JSON')
def machineJSON(technology_id, machine_id):
    machine = session.query(Machine).filter_by(id=machine_id).one()
    return jsonify(machine=machine.serialize)


# Display home page with all technologies
@app.route('/')
@app.route('/technology/')
def display_technologies():
    technologies = session.query(Technology).order_by(asc(Technology.name))
    if 'username' not in login_session:
        return render_template('technology-public.html',
                               technologies=technologies)
    else:
        return render_template('technology.html', technologies=technologies)


# Create a new technology
@app.route('/technology/create/', methods=['GET', 'POST'])
@login_required
def create_technology():
    if request.method == 'POST':
        login_session['user_id'] = get_user_id(login_session['email'])
        create_technology = Technology(name=request.form['name'],
                                       user_id=login_session['user_id'])
        session.add(create_technology)
        session.commit()
        flash('%s Technology Successfully Added' % create_technology.name)
        return redirect(url_for('display_technologies'))
    else:
        return render_template('technology-create.html')


# Edit a selected technology
@app.route('/technology/<int:technology_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_technology(technology_id):
    select_technology = session.query(Technology).filter_by(id=technology_id)\
        .one()
    if select_technology.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('Original Author \
        Login Required!!'); setTimeout(function() {window.location.href = \
        '/technology'}, 500)}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            select_technology.name = request.form['name']
            flash('%s Technology Successfully Updated'
                  % select_technology.name)
            return redirect(url_for('display_technologies'))
    else:
        return render_template('technology-edit.html',
                               technology=select_technology)


# Delete a selected technology
@app.route('/technology/<int:technology_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete_technology(technology_id):
    delete_technology = session.query(Technology).filter_by(id=technology_id)\
        .one()
    if delete_technology.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('Original Author \
        Login Required!!'); setTimeout(function() {window.location.href = \
        '/technology'}, 500)}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(delete_technology)
        session.commit()
        flash('%s Technology Successfully Deleted' % delete_technology.name)
        return redirect(url_for('display_technologies'))
    else:
        return render_template('technology-delete.html',
                               technology=delete_technology)


# Display all machines of a selected technology
@app.route('/technology/<int:technology_id>/')
@app.route('/technology/<int:technology_id>/machine/')
def display_machines(technology_id):
    technology = session.query(Technology).filter_by(id=technology_id).one()
    creator = get_user_info(technology.user_id)
    machines = session.query(Machine).filter_by(technology_id=technology_id).\
        all()
    if 'username' not in login_session:
        return render_template('machines-public.html', machines=machines,
                               technology=technology, creator=creator)
    else:
        return render_template('machines.html', machines=machines,
                               technology=technology, creator=creator)


# Display a selected machine of a selected technology
@app.route('/technology/<int:technology_id>/machine/<int:machine_id>/')
def display_machine(technology_id, machine_id):
    technology = session.query(Technology).filter_by(id=technology_id).one()
    machine = session.query(Machine).filter_by(id=machine_id).one()
    creator = get_user_info(machine.user_id)
    if 'username' not in login_session:
        return render_template('machine-public.html', machine=machine,
                               technology=technology, creator=creator)
    else:
        return render_template('machine.html', machine=machine,
                               technology=technology, creator=creator)


# Add a new machine of a selected technology
@app.route('/technology/<int:technology_id>/machine/create/',
           methods=['GET', 'POST'])
@login_required
def create_machine(technology_id):
    technology = session.query(Technology).filter_by(id=technology_id).one()
    if login_session['user_id'] != technology.user_id:
        return "<script>function myFunction() {alert('Original Author \
        Login Required!!'); setTimeout(function() {window.location.href = \
        '/technology'}, 500)}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        login_session['user_id'] = get_user_id(login_session['email'])
        create_machine = Machine(
            name=request.form['name'],
            manufacturer=request.form['manufacturer'],
            price=request.form['price'],
            feature=request.form['feature'],
            technology_id=technology_id,
            user_id=login_session['user_id'])
        session.add(create_machine)
        session.commit()
        flash('%s Machine Successfully Added' % create_machine.name)
        return redirect(url_for('display_machines',
                        technology_id=technology.id))
    else:
        return render_template('machine-create.html',
                               technology_id=technology.id)


# Edit a selected machine of a selected technology
@app.route('/technology/<int:technology_id>/machine/<int:machine_id>/edit/',
           methods=['GET', 'POST'])
@login_required
def edit_machine(technology_id, machine_id):
    select_technology = session.query(Technology).filter_by(id=technology_id).\
        one()
    select_machine = session.query(Machine).filter_by(id=machine_id).one()
    if select_machine.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('Original Author Login \
        Required!!'); setTimeout(function() {window.location.href = \
        '/technology'}, 500)}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            select_machine.name = request.form['name']
        if request.form['manufacturer']:
            select_machine.manufacturer = request.form['manufacturer']
        if request.form['price']:
            select_machine.price = request.form['price']
        if request.form['feature']:
            select_machine.feature = request.form['feature']
        session.add(select_machine)
        session.commit()
        flash('%s Machine Updated' % select_machine.name)
        return redirect(url_for('display_machines',
                                technology_id=select_technology.id))
    else:
        return render_template('machine-edit.html',
                               technology=select_technology,
                               machine=select_machine)


# Delete a selected machine of a selected technology
@app.route('/technology/<int:technology_id>/machine/<int:machine_id>/delete/',
           methods=['GET', 'POST'])
@login_required
def delete_machine(technology_id, machine_id):
    delete_technology = session.query(Technology).filter_by(id=technology_id)\
        .one()
    delete_machine = session.query(Machine).filter_by(id=machine_id).one()
    if delete_machine.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('Original Author Login \
        Required!!'); setTimeout(function() {window.location.href = \
        '/technology'}, 500)}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(delete_machine)
        session.commit()
        flash('%s Machine Successfully Deleted' % delete_machine.name)
        return redirect(url_for('display_machines',
                        technology_id=delete_technology.id))
    else:
        return render_template('machine-delete.html',
                               technology=delete_technology,
                               machine=delete_machine)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
