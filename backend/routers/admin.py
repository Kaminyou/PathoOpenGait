from flask import Blueprint

admin_api = Blueprint('admin', __name__)


@admin_api.route("/whoami", methods=['GET'])
def admin_whoami():
    return {'msg': 'admin'}
