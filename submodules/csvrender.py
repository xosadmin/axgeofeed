from flask import Blueprint, jsonify, request, Response
from routes import configRead
from utils.query_to_output import query_to_json, build_geofeed_csv
from models.sqlmodel import Users, geofeed
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

csvrender = Blueprint('csvrender', __name__)
sysconfig = configRead("sysconfig")

@csvrender.route("/geofeed/<username>", methods=['GET'])
@csvrender.route("/geofeed/<username>.csv", methods=['GET'])
def showcsvforuser(username):
    checkUserID = Users.query.filter_by(username=username).first()
    if not checkUserID:
        return jsonify({"Status": False, "Message": "No such asset found."}), 404
    userID = checkUserID.id
    rows = geofeed.query.filter_by(userid=userID).all()
    csv_data = build_geofeed_csv(rows)

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=geofeed.csv"
        }
    )

@csvrender.route("/geofeed/json")
def geofeedjson():
    query = geofeed.query.all()
    jsons = query_to_json(query)
    return jsonify(jsons), 200

@csvrender.route("/geofeed/json/<username>", methods=['GET'])
def geofeedjsonforuser(username):
    checkUserID = Users.query.filter_by(username=username).first()
    if not checkUserID:
        return jsonify({"Status": False, "Message": "No such asset found."}), 404
    userID = checkUserID.id
    rows = geofeed.query.filter_by(userid=userID).all()
    jsons = query_to_json(rows)
    return jsonify(jsons), 200

@csvrender.route("/robots.txt")
def robots():
    if sysconfig.get("discourage_crawl", True):
        plaintext = "User-agent: *\nDisallow: /"
    else:
        plaintext = "User-agent: *"
    return Response(plaintext, mimetype="text/plain")
