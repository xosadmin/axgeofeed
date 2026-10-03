from flask import Blueprint, jsonify, request, Response
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
defaults = Blueprint('defaults', __name__)

@defaults.route('/')
def index():
    return jsonify({"Status": False, "Message": "Hello World."}), 200

@defaults.route('/robots.txt')
def robots():
    return Response(
        "User-agent: *\nDisallow: /\n",
        mimetype="text/plain"
    )
