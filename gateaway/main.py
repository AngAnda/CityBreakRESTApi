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

events_url = os.environ.get('EVENTS_SERVICE_URL')
weather_url = os.environ.get('WEATHER_SERVICE_URL')
auth_url = os.environ.get('AUTH_SERVICE_URL')

def authenticate(email, password):
    response = Post(auth_url, json={'email':email, 'password': password})
    return response.status_code == 200

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if auth and authenticate(auth.username, auth.password):
            return f(*args, **kwargs)
        return jsonify({"error": "Authentication required"}), 401
    return decorated_function

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
