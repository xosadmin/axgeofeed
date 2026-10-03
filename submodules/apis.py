from flask import Blueprint, jsonify, request, Response
from utils.ipworks import *
from routes import configRead
from utils.tools import checkIfAPIValid
from models.sqlmodel import db, geofeed, userAsset, apis
from utils.apiconvert import convertGeofeed, convertASSet
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
api = Blueprint('api', __name__)
sysconfig = configRead("sysconfig")

def get_real_ip():
    cf_ip = request.headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip

    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ips = x_forwarded_for.split(',')
        return ips[0]

    ipForOutput = clean_ipaddr(request.remote_addr)
    if not ipForOutput:
        ipForOutput = "169.254.169.254"

    return str(ipForOutput)

def token_to_user(token):
    if not token:
        return {}
    query = apis.query.filter_by(apiToken=token).first()
    if not query:
        return {}
    return {
        "userid": query.userid,
        "ifReadOnly": query.ifReadOnly,
        "isValid": checkIfAPIValid(query.validDate)
    }

@api.route("/api/entry/<action>/<entry_type>", methods=["POST"])
def addentryapi(action, entry_type):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 401
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Invalid Authorization header"}), 401

    token = auth_header.replace("Bearer ", "", 1).strip()
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Missing JSON body"}), 400
    if not isinstance(data, dict):
        return jsonify({"error": "JSON body must be an object"}), 400

    apiInfo = token_to_user(token)

    if not apiInfo:
        return jsonify({"error": "Invalid Token"}), 401
    if not apiInfo.get("isValid", False):
        return jsonify({"error": "Token is not valid"}), 401
    if apiInfo.get("ifReadOnly", True):
        return jsonify({"error": "Insufficient token privilege."}), 403

    if action == "add":
        if entry_type == "geofeed":
            obj = convertGeofeed(data,apiInfo["userid"])
            if not obj:
                return jsonify({"error": "Invalid geofeed data"}), 400
            db.session.add(obj)
        elif entry_type == "asset":
            obj = convertASSet(data,apiInfo["userid"])
            if not obj:
                return jsonify({"error": "Invalid AS-SET data"}), 400
            db.session.add(obj)
        else:
            return jsonify({"error": "Invalid entry type"}), 400
    elif action == "delete":
        if entry_type == "geofeed":
            if "geofeed_id" not in data:
                return jsonify({"error": "Missing geofeed_id"}), 400
            obj = geofeed.query.filter_by(id=data["geofeed_id"],userid=apiInfo["userid"]).first()
            if not obj:
                return jsonify({"error": "Geofeed entry not found"}), 404
            db.session.delete(obj)
        elif entry_type == "asset":
            if "asset_id" not in data:
                return jsonify({"error": "Missing asset_id"}), 400
            obj = userAsset.query.filter_by(id=data["asset_id"],userid=apiInfo["userid"]).first()
            if not obj:
                return jsonify({"error": "AS-SET entry not found"}), 404
            db.session.delete(obj)
        else:
            return jsonify({"error": "Invalid entry type"}), 400
    else:
        return jsonify({"error": "Invalid action"}), 400

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.critical(f"Error when committing to database by API: {e}")
        return jsonify({"status": False, "error": "Database operation failed" }), 500

    return jsonify({"status": True, "action": action, "entry_type": entry_type, "message": "Action completed."}), 200

@api.route("/robots.txt")
def robots():
    if sysconfig.get("discourage_crawl", True):
        plaintext = "User-agent: *\nDisallow: /"
    else:
        plaintext = "User-agent: *"
    return Response(plaintext, mimetype="text/plain")
