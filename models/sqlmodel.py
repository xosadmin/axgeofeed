from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    privilege = db.Column(db.Integer, nullable=False, default=0) # gid=0 -> Full Admin; gid=1 -> API only
    disabled = db.Column(db.Boolean, default=False)

class userAsset(db.Model):
    __tablename__ = 'user_asset'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    asset_name = db.Column(db.String(80), nullable=False)

class geofeed(db.Model):
    __tablename__ = 'geofeed'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assetid = db.Column(db.Integer, db.ForeignKey('user_asset.id'), nullable=False)
    prefix = db.Column(db.String(80), unique=True, nullable=False)
    country_code = db.Column(db.String(2), nullable=False, default='AQ')
    region_code = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    postal_code = db.Column(db.String(80), nullable=True)
