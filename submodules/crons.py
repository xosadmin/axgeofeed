from flask import Blueprint, jsonify, request, Response
from routes import configRead
from utils.ipworks import *
from utils.tools import checkIfAPIValid
from utils.cron import wrapper
from models.sqlmodel import db, geofeed, userAsset, blacklistPrefix, apis
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
crons = Blueprint('crons', __name__)
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

@crons.route("/",methods=["GET"])
def cron():
    userIP = get_real_ip()
    authorisedIP = sysconfig.get("cron_acl",[])
    authorised = False
    if not userIP or not authorisedIP:
        return jsonify({"Status": False, "Message": "Invalid IP Address."}), 403
    for i in authorisedIP:
        if compare_ipaddr(userIP, i):
            authorised = True
            break
    if not authorised:
        return jsonify({"Status": False, "Message": "Insufficient permission to execute task."}), 403
    query = userAsset.query.all()
    queryPrefixList = geofeed.query.all()
    blacklistPrefixList = blacklistPrefix.query.all()
    execute = wrapper(query, queryPrefixList, blacklistPrefixList)
    if not execute and not isinstance(execute, list):
        logging.error(f"Error occurred while performing cron: Wrapper returns null or false")
        return jsonify({"Status": False, "Message": "Task failed."}), 500
    if len(execute) == 0:
        logging.info("Cron: No different compared to last sync.")
        return jsonify({"Status": True, "Message": "No different compared to last sync."}), 200
    try:
        db.session.bulk_save_objects(execute)
        db.session.commit()
        return jsonify({"Status": True, "Message": "Task executed."}), 200
    except Exception as e:
        logging.error(f"Error occurred while performing cron: {e}")
        return jsonify({"Status": False, "Message": "Task failed."}), 500

@crons.route("/ping")
def pingback():
    return jsonify({"Status": True, "Message": "Pong"}), 200

@crons.route("/robots.txt")
def robots():
    if sysconfig.get("discourage_crawl", True):
        plaintext = "User-agent: *\nDisallow: /"
    else:
        plaintext = "User-agent: *"
    return Response(plaintext, mimetype="text/plain")
