from flask import Flask
from .extensions import db
from flask_migrate import Migrate
from app.blueprints.login.routes import  login


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./test.db'


    db.init_app(app)

    app.register_blueprint(login, url_prefix='/login')
    migrate = Migrate()

    return app