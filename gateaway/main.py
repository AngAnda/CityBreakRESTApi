# from flask import *
# from flask_restful import Api, Resource
# import os
# import time
# import datetime
# from requests import get as Get
# from requests import put as Put
# from requests import post as Post
# from requests import delete as Delete
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import current_user, login_user, logout_user, UserMixin
# from wtforms import *
#
# app = Flask('gateway')
# time.sleep(20)
# api = Api(app)
# db = SQLAlchemy(app)
#
# db_user = os.environ.get('DB_USER', 'auth')
# db_pass = os.environ.get('DB_PASSWORD', 'abc123')
# db_host = os.environ.get('DB_HOST', 'auth')
# db_name = os.environ.get('DB_NAME', 'auth')
# PORT = int(os.environ.get('PORT', 5000))
# HOST = os.environ.get('HOST', '0.0.0.0')
#
# db_url = f'mysql://{db_user}:{db_pass}@{db_host}/{db_name}'
#
# app.config['SQLALCHEMY_DATABASE_URI'] = db_url
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SESSION_PERMANENT'] = True
# @app.route('/add_user')
# def add_user():
#     user = User(email="anda.angelescu@gmail.com", password="abc123", name='and')
#     db.session.add(user)
#     db.session.commit()
#
# events_url = os.environ.get('EVENTS_SERVICE_URL')
# weather_url = os.environ.get('WEATHER_SERVICE_URL')
#
# class Citybreak(Resource):
#     def get(self):
#         city = request.args.get('city')
#         date = request.args.get('date', str(datetime.date.today()))
#         if not city:
#             return 'Invalid request: city is missing', 400
#
#         try:
#             events_response = Get(f'{events_url}?city={city}&date={date}', verify=False)
#             events_response.raise_for_status()  # Check for HTTP errors
#             events = events_response.json()
#         except Exception as e:
#             return {'error': f'Failed to fetch events: {str(e)}'}, 500
#
#         try:
#             weather_response = Get(f'{weather_url}?city={city}&date={date}', verify=False)
#             weather_response.raise_for_status()  # Check for HTTP errors
#             weather = weather_response.json()
#         except Exception as e:
#             return {'error': f'Failed to fetch weather: {str(e)}'}, 500
#
#         return {'events': events, 'weather': weather}, 200
#
# req_mapping = {'GET': Get, 'PUT': Put, 'POST': Post, 'DELETE': Delete}
#
# def proxy_request(request, target_url):
#     req = req_mapping[request.method]
#     kwargs = {'url': target_url, 'params': request.args}
#
#     if request.method in ['PUT', 'POST']:
#         kwargs['data'] = request.form
#
#     print(f'KWARGS = {kwargs}')
#
#     response = req(**kwargs)
#     try:
#         response.raise_for_status()
#         return jsonify(response.json()), response.status_code
#     except requests.exceptions.HTTPError as http_err:
#         return jsonify({"error": str(http_err)}), response.status_code if response else 500
#     except requests.exceptions.RequestException as req_err:
#         return jsonify({"error": str(req_err)}), 500
#
# # creez un decorator
# from functools import wraps
# def login_required(f):
#     @wraps(f)
#     def wrapper(*args, **kwargs):
#         if current_user.is_authenticated:
#             return f(*args, **kwargs)
#         else:
#             return redirect(url_for(endpoint='/login', next_url=request.url))
#
# # wrapper peste un formular, este optional, putem si fara el
# # din vt forms
# class LoginForm(Form):
#     def check_existing(form, field):
#         existing = db.session.query(User).filter(User.emai==field.data).first()
#         if not existing:
#             raise ValidationError('Email is not present in the system')
#
#     email = StringField('Email / User', validators=[validators.Required('Email / User is mandatory'),
#                                                     validators.Email(message='Invalid email')])
#     password = PasswordField('Password', validators=[validators.Required('Password is mandatory')])
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     next_url = request.args.get('next_url', '/index')
#     if not is_safe_url(next_url):
#         return abort(400) # bad request
#
#     form = LoginForm(request.form) # de revenit
#     if request.method == 'POST' and form.validate():
#         email = form.email.data
#         password = form.password.data
#         auth = authenticate(email, password)
#         if not auth:
#             app.logger.error(f'Login invalid for {email} and {password}')
#             form.password.errors = ['Email or password incorrect']
#             return render_template('login.html', form=form, next=next_url)
#         else:
#             app.logger.info(f'Login successful for {email}')
#             login_user(LoginUser(email), remember=True, duration=datetime.timedelta(days=30))
#             # user = db.session.query(User).filter(User.email==email).first()
#             session['logged_in'] = True
#             return redirect(next_url, url_for('index'))
#     else:
#         return render_template('login.html', form=form, next_url=next_url)
#
# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(250))
#     password = db.Column(db.String(250))
#     name = db.Column(db.String(250))
#
# class LoginUser(UserMixin):
#     def __init__(self):
#         self.id = id
#
# def authenticate(email, password):
#     if not email or not password:
#         return False
#     result = db.session.query(User).filter(User.email==email).first()
#     return result is not None and result.password==password
#
# # folosesc varianta asta ca sa nu creez un resource de events
# @login_required
# @app.route('/events', methods=['POST', 'PUT', 'DELETE'])
# def handle_events():
#     return proxy_request(request, events_url)
#
# @login_required
# @app.route('/weather', methods=['POST', 'PUT', 'DELETE'])
# def handle_weather():
#     return proxy_request(request, weather_url)
#
# api.add_resource(Citybreak, '/citybreak')
#
#
# with app.app_context():
#     db.create_all()
#
#
# if __name__ == '__main__':
#     app.run(host=os.environ.get('HOST', '0.0.0.0'), port=int(os.environ.get('PORT', 5000)), debug=True)
import os
import time
import datetime
from functools import wraps
from flask import Flask, request, jsonify, abort, redirect, url_for
from flask_restful import Api, Resource
from requests import get as Get, put as Put, post as Post, delete as Delete

app = Flask('gateway')
time.sleep(20)
api = Api(app)

# Lista de utilizatori predefiniți
users = [
    {"email": "user1@example.com", "password": "password1"},
    {"email": "user2@example.com", "password": "password2"}
]

# Configurarea URL-urilor serviciilor externe
events_url = os.environ.get('EVENTS_SERVICE_URL')
weather_url = os.environ.get('WEATHER_SERVICE_URL')

# Funcția de autentificare
def authenticate(email, password):
    for user in users:
        if user["email"] == email and user["password"] == password:
            return True
    return False

# Decoratorul pentru autentificare
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if auth and authenticate(auth.username, auth.password):
            return f(*args, **kwargs)
        return jsonify({"error": "Authentication required"}), 401
    return decorated_function

# Clasa Citybreak pentru API-ul RESTful
class Citybreak(Resource):
    @login_required
    def get(self):
        city = request.args.get('city')
        date = request.args.get('date', str(datetime.date.today()))
        if not city:
            return 'Invalid request: city is missing', 400

        try:
            events_response = Get(f'{events_url}?city={city}&date={date}', verify=False)
            events_response.raise_for_status()  # Check for HTTP errors
            events = events_response.json()
        except Exception as e:
            return {'error': f'Failed to fetch events: {str(e)}'}, 500

        try:
            weather_response = Get(f'{weather_url}?city={city}&date={date}', verify=False)
            weather_response.raise_for_status()  # Check for HTTP errors
            weather = weather_response.json()
        except Exception as e:
            return {'error': f'Failed to fetch weather: {str(e)}'}, 500

        return {'events': events, 'weather': weather}, 200

# Funcția pentru a face proxy request
req_mapping = {'GET': Get, 'PUT': Put, 'POST': Post, 'DELETE': Delete}

def proxy_request(request, target_url):
    req = req_mapping[request.method]
    kwargs = {'url': target_url, 'params': request.args}

    if request.method in ['PUT', 'POST']:
        kwargs['data'] = request.form

    print(f'KWARGS = {kwargs}')

    response = req(**kwargs)
    try:
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": str(http_err)}), response.status_code if response else 500
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": str(req_err)}), 500

# Rutele pentru proxy request
@app.route('/events', methods=['POST', 'PUT', 'DELETE', 'GET'])
@login_required
def handle_events():
    return proxy_request(request, events_url)

@app.route('/weather', methods=['POST', 'PUT', 'DELETE'])
@login_required
def handle_weather():
    return proxy_request(request, weather_url)

api.add_resource(Citybreak, '/citybreak')

# Rularea aplicației
if __name__ == '__main__':
    app.run(host=os.environ.get('HOST', '0.0.0.0'), port=int(os.environ.get('PORT', 5000)), debug=True)
