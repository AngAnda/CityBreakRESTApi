from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os

app = Flask('auth_service')
api = Api(app)

db_user = os.environ.get('DB_USER', 'auth')
db_pass = os.environ.get('DB_PASSWORD', 'abc123')
db_host = os.environ.get('DB_HOST', 'auth')
db_name = os.environ.get('DB_NAME', 'auth')
PORT = int(os.environ.get('PORT', 5000))
HOST = os.environ.get('HOST', '0.0.0.0')

db_url = f'mysql://{db_user}:{db_pass}@{db_host}/{db_name}'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url


users = [
    {"email": "user1@example.com", "password": "password1"},
    {"email": "user2@example.com", "password": "password2"}
]

class Auth(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        for user in users:
            if user["email"] == email and user["password"] == password:
                    return jsonify({"message": "Authenticated"})

        return jsonify({"error": "Authentication failed"}), 401


api.add_resource(Auth, '/auth')

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)