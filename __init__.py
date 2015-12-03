from flask import Flask 
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__, static_url_path='/templates/static')
app.config["MONGODB_SETTINGS"] = {'DB': "voteaqui"}
app.config["SECRET_KEY"] = "KeepThisS3cr3t"

db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db) # sessions w/ mongoengine

# Flask BCrypt will be used to salt the user password
flask_bcrypt = Bcrypt(app)

# Associate Flask-Login manager with current app
login_manager = LoginManager()
login_manager.init_app(app)

def register_blueprints(app):
	from voteaqui.views import polls
	from auth import auth_flask_login
	app.register_blueprint(polls)
	app.register_blueprint(auth_flask_login)

register_blueprints(app)

if __name__ == '__main__':
	app.run()