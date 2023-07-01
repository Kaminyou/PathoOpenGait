from flask import Flask
from flask_cors import CORS


from routers.admin import admin_api
from routers.demo import demo_api

app = Flask(__name__)
CORS(app)

# 首頁
@app.route("/api/version", methods=['GET'])
def version():
    return {
        'version': '1.0.0',
    }

app.register_blueprint(admin_api, url_prefix='/api/admin')
app.register_blueprint(demo_api, url_prefix='/api/demo')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)