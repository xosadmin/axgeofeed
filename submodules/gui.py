import sys
from sqlalchemy import update
from routes import configRead
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, current_user, login_required, logout_user
from submodules.logins import login_manager
from utils.ipworks import *
from utils.bcryptworks import verifyPassword, encrypt_password, encrypt_hash_base64
from utils.tools import uuidGen, userIDGen, factor_disable, dateConvert, checkIfAPIValid
from utils.assetworks import sanitize_asset
from utils.cron import manualRefresh
from models.formModel import (LoginForm, addEditForm, addEditUserForm, addEditASSet,
                              addEditBlackListPrefix, addAPI, addEditPrfxLenForm)
from models.loginModel import *
from models.sqlmodel import db, Users, geofeed, userAsset, blacklistPrefix, apis, prefixlen
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
guis = Blueprint('guis', __name__)
sysconfig = configRead("sysconfig")

if len(sysconfig) == 0:
    logging.critical("System config is empty.")
    sys.exit(1)

# Ready to fly

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

@login_manager.user_loader
def load_user(user_id):
    query = Users.query.get(user_id)
    if not query:
        return None
    logging.info(f"User {query.id} (Privilege: {query.privilege}) logged in.")
    return User(query.id, query.privilege)

@guis.route("/", methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('.dashboard'))
    form = LoginForm()
    if request.method == 'GET':
        return render_template("login.html", form=form)
    else:
        username = form.username.data
        password = form.password.data
        query = Users.query.filter_by(username=username).first()
        if not query:
            return "<script>alert('Invalid Credentials.');history.back();</script>"
        correct_password = query.password
        if query.disabled:
            return "<script>alert('User is disabled.');history.back();</script>"
        if query.privilege > 1:
            return "<script>alert('User doesn't have permission to access GUI.');history.back();</script>"
        if_Verify = verifyPassword(password, correct_password)
        if not if_Verify:
            return "<script>alert('Invalid Credentials.');history.back();</script>"
        user = User(query.id, query.privilege)
        login_user(user)
        logging.info(f"User {username} is logged in.")
        return redirect(url_for('.dashboard'))

@guis.route("/dashboard")
@login_required
def dashboard():
    privileged = False
    current_user_id = current_user.id
    current_user_role = current_user.role
    if current_user_role == 0:
        query = geofeed.query.all()
        privileged = True
    else:
        query = geofeed.query.filter_by(userid=current_user_id).all()

    query = sorted(query, key=sort_prefix)

    username = Users.query.filter_by(id=current_user_id).first().username
    return render_template("dashboard.html", query=query, username=username, privileged=privileged)

@guis.route("/addprefix")
@login_required
def addprefix():
    form = addEditForm()
    return render_template("addedit.html", form=form, action="add")

@guis.route("/prefixaction/<action>/<prefixid>")
@login_required
def prefixaction(action, prefixid):
    currentuserid = current_user.id
    form = addEditForm()
    if action == "edit":
        queryPrefix = geofeed.query.filter_by(id=prefixid, userid=currentuserid).first()
        if not queryPrefix:
            return "<script>alert('Cannot find specified prefix.');history.back();</script>"
        form.prefix.data = queryPrefix.prefix
        form.display.data = queryPrefix.included_in_geofeed
        form.country_code.data = queryPrefix.country_code
        form.region_code.data = queryPrefix.region_code
        form.city.data = queryPrefix.city
        form.postal_code.data = queryPrefix.postal_code
        return render_template(
            "addedit.html",
            form=form,
            action=action,
            prefix=queryPrefix.prefix
        )
    return render_template("addedit.html", form=form, action=action)
# GUI Rendering

@guis.route("/editgeofeed", methods=['POST'])
@login_required
def editgeofeed():
    try:
        form = addEditForm()
        if form.validate_on_submit():
            prefix = form.prefix.data
            ifdisplay = factor_disable(form.display.data)
            country_code = form.country_code.data.upper()
            region_code = form.region_code.data.upper()
            city = form.city.data.capitalize()
            postal_code = form.postal_code.data.upper()
            queryPrefix = geofeed.query.filter_by(prefix=prefix).first()
            if not is_valid_cidr(prefix):
                return "<script>alert('Invalid CIDR.');window.location.href='/gui/dashboard';</script>"
            if not queryPrefix:
                uniqID = userIDGen()
                commit = geofeed(id=uniqID, userid=current_user.id, assetid=current_user.id, prefix=prefix,
                                 included_in_geofeed=ifdisplay, country_code=country_code, region_code=region_code,
                                 city=city,postal_code=postal_code)
                db.session.add(commit)
            else:
                db.session.execute(update(geofeed).filter_by(prefix=prefix).values(
                    included_in_geofeed=ifdisplay, country_code=country_code, region_code=region_code,
                                                                         city=city, postal_code=postal_code))
            db.session.commit()
            return "<script>alert('Update successful.');window.location.href='/gui/dashboard';</script>"
        else:
            logging.error(f"Form is invalid.")
            return "<script>alert('System error occurred. This action is not performed.');window.location.href='/gui/dashboard';</script>"
    except Exception as e:
        logging.error(f"Error occurred while performing action: {e}")
        return "<script>alert('System error occurred. This action is not performed.');window.location.href='/gui/dashboard';</script>"

@guis.route("/deleteprefix/<prefixid>")
@login_required
def deleteprefix(prefixid):
    current_user_id = current_user.id
    current_user_role = current_user.role
    query = geofeed.query.filter_by(id=prefixid).first()
    if not query:
        return "<script>alert('No such prefix, or you do not have such permission to perform action.');history.back();</script>"
    if current_user_role != 0 and current_user_id != query.userid:
        return "<script>alert('No such prefix, or you do not have such permission to perform action.');history.back();</script>"
    db.session.delete(query)
    db.session.commit()
    return "<script>alert('Delete successful.');window.location.href='/gui/dashboard';</script>"

@guis.route("/users")
@login_required
def usersboard():
    current_user_id = current_user.id
    current_user_privilege = current_user.role
    query = Users.query.all()
    if current_user_privilege == 0:
        return render_template("userlist.html",userrole=current_user_privilege,userID=current_user_id,query=query)
    else:
        return "<script>alert('You do not have such permission to perform action.');history.back();</script>"

@guis.route("/adduser", methods=['GET','POST'])
@login_required
def adduser():
    current_user_privilege = current_user.role
    if current_user_privilege != 0:
        return "<script>alert('You do not have such permission to perform action.');history.back();</script>"
    form = addEditUserForm()
    if request.method == "GET":
        return render_template("addedituser.html",form=form)
    else:
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            repeat_password = form.repeat_password.data
            privilege = form.privilege.data
            disabled = factor_disable(form.disabled.data)
            if not password or not repeat_password:
                return "<script>alert('Passwords is empty.');history.back();</script>"
            if password != repeat_password:
                return "<script>alert('Passwords do not match.');history.back();</script>"
            userID = userIDGen()
            encoded_password = encrypt_hash_base64(encrypt_password(password))
            newQuery = [Users(id=userID, username=username, password=encoded_password, privilege=privilege, disabled=disabled),
                        userAsset(id=userID, userid=userID, asset_name=f"{username}_MANUAL", systemCreated=True)]
            db.session.bulk_save_objects(newQuery)
            db.session.commit()
            return "<script>alert('User registration successful.');window.location.href='/gui/dashboard';</script>"
        else:
            logging.error(f"Form is invalid.")
            return "<script>alert('System error is occurred.');history.back();</script>"

@guis.route("/edituser/<userid>", methods=['GET','POST'])
@login_required
def edituser(userid):
    current_user_id = current_user.id
    current_user_privilege = current_user.role
    if current_user_privilege != 0 and current_user_id != userid:
        return "<script>alert('You do not have such permission to perform action.');history.back();</script>"
    form = addEditUserForm()
    if request.method == "GET":
        query = Users.query.filter_by(id=userid).first()
        if not query:
            return "<script>alert('No such user.');history.back();</script>"
        form.username.data = query.username
        form.privilege.data = query.privilege
        form.disabled.data = query.disabled
        return render_template("addedituser.html", form=form, userid=query.id)
    else:
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            repeat_password = form.repeat_password.data
            privilege = form.privilege.data
            disabled = factor_disable(form.disabled.data)
            if password != repeat_password:
                return "<script>alert('Passwords do not match.');history.back();</script>"
            if current_user_id == userid and disabled == 1:
                return "<script>alert('Cannot disable yourself.');history.back();</script>"
            if current_user_id == userid and int(privilege) != int(current_user_privilege):
                return "<script>alert('Cannot change privilege for yourself.');history.back();</script>"
            if not password:
                db.session.execute(update(Users).filter_by(id=userid).values(username=username,privilege=privilege,
                                                                             disabled=disabled))
            else:
                encoded_password = encrypt_hash_base64(encrypt_password(password))
                db.session.execute(update(Users).filter_by(id=userid).values(username=username,password=encoded_password,
                                                                                privilege=privilege,disabled=disabled))
            db.session.commit()
            return "<script>alert('Edit successful.');window.location.href='/gui/users';</script>"
        else:
            logging.error(f"Form is invalid.")
            return "<script>alert('System error is occurred.');history.back();</script>"

@guis.route("/useraction/<action>/<userid>")
@login_required
def useraction(action,userid):
    current_user_id = current_user.id
    current_user_privilege = current_user.role
    if current_user_privilege != 0:
        return "<script>alert('You do not have such permission to perform action.');history.back();</script>"
    query = Users.query.filter_by(id=userid).first()
    if not query:
        return "<script>alert('No such user.');history.back();</script>"
    if current_user_id == userid:
        return f"<script>alert('You cannot {action} yourself.');history.back();</script>"
    if action == "delete":
        geofeed.query.filter_by(userid=userid).delete()
        userAsset.query.filter_by(userid=userid).delete()
        db.session.delete(query)
        db.session.commit()
        return "<script>alert('Delete successful.');window.location.href='/gui/users';</script>"
    elif action == "disable":
        db.session.execute(update(Users).filter_by(id=userid).values(disabled=True))
        db.session.commit()
        return "<script>alert('Disable successful.');window.location.href='/gui/users';</script>"
    elif action == "enable":
        db.session.execute(update(Users).filter_by(id=userid).values(disabled=False))
        db.session.commit()
        return "<script>alert('Enable successful.');window.location.href='/gui/users';</script>"
    else:
        return "<script>alert('Unknown Action.');history.back();</script>"

@guis.route("/syncprefix")
@login_required
def syncprefix():
    current_user_id = current_user.id
    query = userAsset.query.filter_by(userid=current_user_id).all()
    blacklistPrefixList = blacklistPrefix.query.filter_by(userid=current_user_id).all()
    existingPrefix = geofeed.query.filter_by(userid=current_user_id).all()
    if not query:
        return "<script>alert('No AS-SET associated with this user.');history.back();</script>"
    if len(query) == 1 and query[0].asset_name.endswith("_MANUAL"):
        return "<script>alert('No valid AS-SET. Please setup AS-SET in your dashboard.');history.back();</script>"
    outputs = manualRefresh(query, existingPrefix, blacklistPrefixList)
    db.session.bulk_save_objects(outputs)
    db.session.commit()
    return ("<script>alert('Refresh process has been added to task list. It may take a few minutes.');"
            "window.location.href='/gui/dashboard';</script>")

@guis.route("/assets")
@login_required
def assets():
    privileged = False
    current_user_id = current_user.id
    current_user_role = current_user.role
    if current_user_role == 0:
        query = userAsset.query.all()
        privileged = True
    else:
        query = userAsset.query.filter_by(userid=current_user_id).all()
    return render_template("assetlist.html",query=query,userid=current_user_id,privileged=privileged)

@guis.route("/addasset", methods=['GET','POST'])
@login_required
def addasset():
    current_user_id = current_user.id
    form = addEditASSet()
    if request.method == "GET":
        return render_template("addeditasset.html",form=form)
    else:
        if form.validate_on_submit():
            asset_name = form.asset_name.data
            lookup_existing = userAsset.query.filter_by(asset_name=asset_name).first()
            if lookup_existing:
                return ("<script>alert('AS-SET is added by other user. Please contact admin for assistant.');"
                        "window.location.href='/gui/assets';</script>")
            asset_name = sanitize_asset(asset_name)
            if asset_name is None:
                return "<script>alert('Invalid AS-SET Entry.');window.location.href='/gui/assets';</script>"
            newQuery = userAsset(userid=current_user_id,asset_name=asset_name,systemCreated=False)
            db.session.add(newQuery)
            db.session.commit()
            return "<script>alert('AS-SET added successfully.');window.location.href='/gui/assets';</script>"
        else:
            logging.error(f"Form is invalid.")
            return "<script>alert('System error is occurred.');history.back();</script>"

@guis.route("/deleteasset/<id>")
@login_required
def deleteasset(id):
    current_user_id = current_user.id
    current_user_role = current_user.role
    query = userAsset.query.filter_by(id=id).first()
    if not query:
        return "<script>alert('No such AS-SET.');history.back();</script>"
    if current_user_role != 0 and current_user_id != query.userid:
        return f"<script>alert('You don't have permission to delete this AS-SET.');history.back();</script>"
    if query.systemCreated:
        return f"<script>alert('Cannot delete system generated AS-SET.');history.back();</script>"
    db.session.delete(query)
    db.session.commit()
    return "<script>alert('Delete successful.');window.location.href='/gui/assets';</script>"

@guis.route("/prefixlen")
@login_required
def showprefixlen():
    privileged = False
    current_user_id = current_user.id
    current_user_role = current_user.role
    if current_user_role == 0:
        query = prefixlen.query.all()
        privileged = True
    else:
        query = prefixlen.query.filter_by(userid=current_user_id).all()
    return render_template("prefixlen.html",query=query,userid=current_user_id,privileged=privileged)

@guis.route("/addprefixlen", methods=['GET','POST'])
@login_required
def addprefixlen():
    current_user_id = current_user.id
    form = addEditPrfxLenForm()
    if request.method == "GET":
        return render_template("addedit_prefixlen.html",form=form)
    else:
        if form.validate_on_submit():
            prefix = form.prefix.data
            allocation_len = form.allocation_len.data
            site_count = form.site_count.data
            lookup_existing = prefixlen.query.filter_by(prefix=prefix).prefix()
            if lookup_existing:
                return ("<script>alert('Prefixlen entry is added by other user. Please contact admin for assistant.');"
                        "window.location.href='/gui/prefixlen';</script>")
            maxlen = 1
            if check_ip_version(prefix) == 4:
                maxlen = 32
            elif check_ip_version(prefix) == 6:
                maxlen = 128
            if allocation_len and (allocation_len < 1 or allocation_len > maxlen):
                return ("<script>alert('Invalid allocation length!');"
                        "window.location.href='/gui/prefixlen';</script>")
            newQuery = prefixlen(userid=current_user_id,prefix=prefix,allocation_len=allocation_len,site_count=site_count)
            db.session.add(newQuery)
            db.session.commit()
            return "<script>alert('Prefixlen entry added successfully.');window.location.href='/gui/prefixlen';</script>"
        else:
            logging.error(f"Form is invalid.")
            return "<script>alert('System error is occurred.');history.back();</script>"

@guis.route("/deleteprefixlen/<id>")
@login_required
def deleteprefixlen(id):
    current_user_id = current_user.id
    current_user_role = current_user.role
    query = prefixlen.query.filter_by(id=id).first()
    if not query:
        return "<script>alert('No such entry.');history.back();</script>"
    if current_user_role != 0 and current_user_id != query.userid:
        return f"<script>alert('You don't have permission to delete this entry.');history.back();</script>"
    db.session.delete(query)
    db.session.commit()
    return "<script>alert('Delete successful.');window.location.href='/gui/prefixlen';</script>"

@guis.route("/blacklistprefix")
@login_required
def blacklistprefix():
    privileged = False
    current_user_id = current_user.id
    current_user_role = current_user.role
    if current_user_role == 0:
        query = blacklistPrefix.query.all()
        privileged = True
    else:
        query = blacklistPrefix.query.filter_by(userid=current_user_id).all()
    return render_template("blacklist_prefix_list.html",query=query,
                           userid=current_user_id,privileged=privileged)

@guis.route("/addblacklistprefix", methods=['GET','POST'])
@login_required
def addblacklistprefix():
    current_user_id = current_user.id
    form = addEditBlackListPrefix()
    if request.method == "GET":
        return render_template("add_edit_blacklist_prefix.html", form=form)
    else:
        if form.validate_on_submit():
            prefix = form.prefix.data
            if not is_valid_cidr(prefix):
                return "<script>alert('Invalid CIDR.');history.back();</script>"
            checkIfExist = blacklistPrefix.query.filter_by(prefix=prefix).first()
            if checkIfExist:
                return "<script>alert('The prefix is added by other user.');history.back();</script>"
            newQuery = blacklistPrefix(userid=current_user_id,prefix=prefix)
            db.session.add(newQuery)
            db.session.commit()
            return "<script>alert('Added successfully.');window.location.href='/gui/blacklistprefix';</script>"
        else:
            logging.error(f"Form is invalid.")
            return "<script>alert('System Error Occurred.');history.back();</script>"

@guis.route("/deleteblacklistprefix/<id>")
@login_required
def deleteblacklistprefix(id):
    current_user_id = current_user.id
    current_user_role = current_user.role
    query = blacklistPrefix.query.filter_by(id=id).first()
    if not query:
        return "<script>alert('No such prefix.');history.back();</script>"
    if current_user_role != 0 and current_user_id != query.userid:
        return f"<script>alert('You don't have permission to delete this prefix.');history.back();</script>"
    db.session.delete(query)
    db.session.commit()
    return "<script>alert('Delete successful.');window.location.href='/gui/blacklistprefix';</script>"

@guis.route("/apis")
@login_required
def apisDashboard():
    current_user_id = current_user.id
    current_user_role = current_user.role
    privileged = False
    if current_user_role == 0:
        privileged = True
    try:
        query = apis.query.filter_by(userid=current_user_id).all()
        return render_template("apis.html",query=query,privileged=privileged)
    except Exception as e:
        logging.error(f"Error when fetching API: {e}")
        return "<script>alert('System Error Occurred.');history.back();</script>"

@guis.route("/addapi", methods=['GET','POST'])
@login_required
def addapis():
    form = addAPI()
    if request.method == "GET":
        return render_template("addapi.html",form=form)
    current_user_id = current_user.id
    try:
        if form.validate_on_submit():
            ifReadOnly = factor_disable(form.readonly.data)
            validDate = form.validDate.data
            validDate_converted = dateConvert(validDate)
            if not validDate_converted:
                return "<script>alert('Invalid Date.');history.back();</script>"
            tokenID = uuidGen()
            newQuery = apis(apiToken=tokenID,userid=current_user_id,
                            ifReadOnly=ifReadOnly,validDate=validDate_converted)
            db.session.add(newQuery)
            db.session.commit()
            return render_template("showapi.html",tokenID=tokenID)
        else:
            logging.error(f"Form is invalid.")
            return "<script>alert('System Error Occurred.');history.back();</script>"
    except Exception as e:
        logging.critical(f"Error when adding API: {e}")
        return "<script>alert('System Error Occurred.');history.back();</script>"

@guis.route("/deleteapi/<id>")
@login_required
def deleteapi(id):
    current_user_id = current_user.id
    current_user_role = current_user.role
    query = apis.query.filter_by(id=id).first()
    if not query:
        return "<script>alert('No such API Token.');history.back();</script>"
    if current_user_role != 0 and current_user_id != query.userid:
        return f"<script>alert('You don't have permission to delete this prefix.');history.back();</script>"
    db.session.delete(query)
    db.session.commit()
    return "<script>alert('Delete successful.');window.location.href='/gui/apis';</script>"

@guis.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("logout.html")
