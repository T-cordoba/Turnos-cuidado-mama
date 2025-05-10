from flask import Flask
from .db import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    init_db(app)

    from .routes import main
    app.register_blueprint(main)

    return app