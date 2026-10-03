from flask import Blueprint, redirect, Response
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
defaults = Blueprint('defaults', __name__)

@defaults.route("/")
def index():
    return redirect("/gui/", code=301)

@defaults.route('/robots.txt')
def robots():
    return Response(
        "User-agent: *\nDisallow: /\n",
        mimetype="text/plain"
    )
