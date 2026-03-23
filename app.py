import os,sys
from flask import Flask, jsonify, render_template, request, redirect, url_for, Response
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from sqlalchemy import update
from utils.ipworks import *
from utils.bcryptworks import verifyPassword
from models.formModel import LoginForm, addEditForm
from models.loginModel import *
from utils.yamlworks import readConf
from utils.tools import uuidGen
from utils.query_to_output import query_to_json, build_geofeed_csv
from models.sqlmodel import db, User, geofeed, userAsset
import logging

if not os.path.exists(os.path.join(os.getcwd(),'config.yaml')):
    logging.critical("No config.yaml found.")
    sys.exit(1)

configInfo = readConf("config.yaml")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
sqlinfo = configInfo.get("database",{})

if len(sqlinfo) == 0:
    logging.critical("No database information defined.")
    sys.exit(1)

db_uri = (
    f"mysql+pymysql://{sqlinfo['username']}:{sqlinfo['password']}@"
    f"{sqlinfo['server']}:{sqlinfo['port']}/{sqlinfo['dbname']}"
)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SECRET_KEY'] = uuidGen()
db.init_app(app)

login_manager = LoginManager()

sysconfig = configInfo.get("sysconfig",{})
if len(sysconfig) == 0:
    logging.critical("System config is empty.")
    sys.exit(1)

# Ready to fly

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route("/", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if request.method == 'GET':
        return render_template("login.html")
    else:
        username = form.username.data
        password = form.password.data
        query = User.query.filter_by(username=username).first()
        if not query:
            return "<script>alert('Invalid Credentials.');history.back;</script>"
        correct_password = query.password
        if_Verify = verifyPassword(password, correct_password)
        if not if_Verify:
            return "<script>alert('Invalid Credentials.');history.back;</script>"
        user = User(query.id)
        login_user(user)
        logging.info(f"User {username} is logged in.")
        return redirect(url_for('dashboard'))

@app.route("/dashboard")
@login_required
def dashboard():
    query = geofeed.query.all()
    return render_template("dashboard.html",query=query)

@app.route("/addprefix")
@login_required
def addprefix():
    form = addEditForm()
    return render_template("addedit.html", form=form, action="add")

@app.route("/prefixaction/<action>/<prefix>")
@login_required
def prefixaction(action, prefix):
    currentuserid = current_user.id
    if not is_valid_cidr(prefix):
        return "<script>alert('Invalid CIDR.');history.back;</script>"
    form = addEditForm()
    if action == "edit":
        queryPrefix = geofeed.query.filter_by(prefix=prefix, userid=currentuserid).first()
        if not queryPrefix:
            return render_template("addedit.html", form=form, action=action)
        form.prefix.data = queryPrefix.prefix
        form.country_code.data = queryPrefix.country_code
        form.region_code.data = queryPrefix.region_code
        form.city.data = queryPrefix.city
        form.postal_code.data = queryPrefix.postal_code
        return render_template(
            "addedit.html",
            form=form,
            action=action,
            prefix=prefix
        )
    return render_template("addedit.html", form=form, action=action)

@app.route("/doaction", methods=['POST'])
@login_required
def doaction():
    try:
        form = addEditForm()
        prefix = form.prefix.data
        country_code = form.country_code.data
        region_code = form.region_code.data
        city = form.city.data
        postal_code = form.postal_code.data
        queryPrefix = geofeed.query.filter_by(prefix=prefix).first()
        if not is_valid_cidr(prefix):
            return "<script>alert('Invalid CIDR.');history.back;</script>"
        if not queryPrefix:
            commit = geofeed(userid=current_user.id,country_code=country_code,
                             region_code=region_code,city=city,postal_code=postal_code)
        else:
            commit = update(geofeed).filter_by(prefix=prefix).values(country_code=country_code,
                                                                     region_code=region_code,
                                                                     city=city,
                                                                     postal_code=postal_code
                                                                     )
        db.session.add(commit)
        db.session.commit()
        return "<script>alert('Update successful.');window.location.href='/dashboard';</script>"
    except Exception as e:
        logging.error(f"Error occurred while performing action: {e}")
        return "<script>alert('System error occurred. This action is not performed.');window.location.href='/dashboard';</script>"

@app.route("/delete/<prefix>")
@login_required
def delete(prefix):
    current_user_id = current_user.id
    query = geofeed.query.filter_by(prefix=prefix,userid=current_user_id).first()
    if not query:
        return "<script>alert('No such prefix, or you do not have such permission to perform action.');history.back;</script>"
    db.session.delete(query)
    db.session.commit()
    return "<script>alert('Delete successful.');window.location.href='/dashboard';</script>"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("logout.html")

@app.route("/geofeed")
def showcsv():
    rows = geofeed.query.all()
    csv_data = build_geofeed_csv(rows)

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=geofeed.csv"
        }
    )

@app.route("/geofeed/<asset>", methods=['GET'])
def showcsvforasset(asset):
    checkASSETID = userAsset.query.filter_by(asset_name=asset).first()
    if not checkASSETID:
        return jsonify({"Status": False, "Message": "No such asset found."}), 404
    assetID = checkASSETID.id
    rows = geofeed.query.filter_by(assetid=assetID).all()
    csv_data = build_geofeed_csv(rows)

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=geofeed.csv"
        }
    )

@app.route("/geofeed/json")
def geofeedjson():
    query = geofeed.query.all()
    jsons = query_to_json(query)
    return jsonify(jsons), 200

@app.route("/geofeed/json/<asset>", methods=['GET'])
def geofeedjsonforasset(asset):
    checkASSETID = userAsset.query.filter_by(asset_name=asset).first()
    if not checkASSETID:
        return jsonify({"Status": False, "Message": "No such asset found."}), 404
    assetID = checkASSETID.id
    rows = geofeed.query.filter_by(assetid=assetID).all()
    jsons = query_to_json(rows)
    return jsonify(jsons), 200

@app.route("/robots.txt")
def robots():
    if sysconfig.get("discourage_crawl", True):
        plaintext = "User-agent: *\nDisallow: /"
    else:
        plaintext = "User-agent: *"
    return Response(plaintext, mimetype="text/plain")

@app.errorhandler(Exception)
def internal_server_error(error):
    logger.error("Error occurred: %s", error, exc_info=True)
    return jsonify({
        'status': False,
        'message': 'System cannot handle your request',
    }), 500

if __name__ == "__main__":
    app.run(debug=True)