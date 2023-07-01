import json
import os
from datetime import datetime, timedelta, timezone

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import (JWTManager, create_access_token, get_jwt,
                                get_jwt_identity)

from db import db
from routers.admin import admin_api
from routers.demo import demo_api
from routers.token import token_api
from routers.user import user_api

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY',)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

jwt = JWTManager(app)
CORS(app)
db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()['exp']
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data['access_token'] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@app.route("/api/version", methods=['GET'])
def version():
    return {
        'version': '1.0.0',
    }


app.register_blueprint(admin_api, url_prefix='/api/admin')
app.register_blueprint(demo_api, url_prefix='/api/demo')
app.register_blueprint(token_api, url_prefix='/api/token')
app.register_blueprint(user_api, url_prefix='/api/user')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
