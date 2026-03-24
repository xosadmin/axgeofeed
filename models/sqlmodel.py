from utils.tools import userIDGen
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(80), primary_key=True, default=userIDGen)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    privilege = db.Column(db.Integer, nullable=False, default=0) # gid=0 -> Full Admin; gid=1 -> ordinary user; gid=2 -> API only
    disabled = db.Column(db.Boolean, default=False)

class userAsset(db.Model):
    __tablename__ = 'user_asset'
    id = db.Column(db.String(80), primary_key=True, default=userIDGen)
    userid = db.Column(db.String(80), db.ForeignKey('users.id'), nullable=False)
    asset_name = db.Column(db.String(80), nullable=False)
    systemCreated = db.Column(db.Boolean, nullable=False, default=False)

class geofeed(db.Model):
    __tablename__ = 'geofeed'
    id = db.Column(db.String(80), primary_key=True, default=userIDGen)
    userid = db.Column(db.String(80), db.ForeignKey('users.id'), nullable=False)
    assetid = db.Column(db.String(80), db.ForeignKey('user_asset.id'), nullable=False)
    included_in_geofeed = db.Column(db.Boolean, nullable=False, default=True)
    prefix = db.Column(db.String(80), unique=True, nullable=False)
    country_code = db.Column(db.String(2), nullable=False, default='AQ')
    region_code = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    postal_code = db.Column(db.String(80), nullable=True)
