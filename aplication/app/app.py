from flask import Flask
from .extensions import db, login_manager, bcrypt
from .extensions import login_manager
from flask_migrate import Migrate

from app.blueprints.login.routes import login as login_blueprint
from app.blueprints.login.models import User


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./application.db'
    app.secret_key = 'promo-week-consorcios-sicoob-moeda-danilo-13'

    db.init_app(app)

    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    bcrypt.init_app(app)

    app.register_blueprint(login_blueprint, url_prefix='/login')
    migrate = Migrate(app, db)

    return app