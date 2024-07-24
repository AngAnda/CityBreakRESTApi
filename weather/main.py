from flask import Flask, request
from flask_restful import Api, Resource
import json
import os
import logging
import datetime
import time
import redis

app = Flask('weather')
time.sleep(20)
api = Api(app)
client = redis.Redis(host=os.environ.get('REDIS_HOST', 'localhost'))

# Preîncărcare date în Redis la inițializarea aplicației
preload_data = {
    "Brasov-2024-07-24": {
        "temperature": "22°C",
        "humidity": "60%",
        "wind": "10 km/h"
    },
    "Brasov": {
        "temperature": "20°C",
        "humidity": "55%",
        "wind": "8 km/h"
    }
}

for key, value in preload_data.items():
    client.set(key, json.dumps(value))

class Weather(Resource):
    def get(self):
        city = request.args.get("city")
        date = request.args.get("date")

        if not city and not date:
            all_keys = client.keys('*')
            all_weather = {}
            for key in all_keys:
                weather = client.get(key).decode('utf-8')
                all_weather[key.decode('utf-8')] = json.loads(weather)
            return all_weather, 200

        key = f'{city}-{date}' if date else city
        weather = client.get(key)
        if weather:
            weather = weather.decode('utf-8')
            weather = json.loads(weather)
            return weather, 200
        else:
            return {"error": "Data not found"}, 404

    def post(self):
        keys = ('temperature', 'humidity', 'wind')
        weather = {k: request.form.get(k) for k in keys}
        city = request.form.get('city', 'Brasov')
        date = request.form.get('date', str(datetime.date.today()))
        key = f'{city}-{date}' if date else city
        client.set(key, json.dumps(weather))
        return 'OK', 200

api.add_resource(Weather, '/weather')

if __name__ == '__main__':
    app.run(host=os.environ.get('HOST', '0.0.0.0'), port=int(os.environ.get('PORT', 5000)), debug=True)
