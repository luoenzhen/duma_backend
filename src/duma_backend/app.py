import os
import os.path

from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_migrate import Migrate
from flask_tern import logging as app_logging
from flask_tern.utils.config import load_settings

# from flask_tern.utils.json import TernJSONEncoder
from werkzeug.middleware.proxy_fix import ProxyFix

from duma_backend.version import version


def create_app(config=None) -> Flask:
    ###################################################
    # Setup Flask App
    ###################################################
    app = Flask("duma_backend")
    app.config["VERSION"] = version

    ###################################################
    # custom json encoder
    ###################################################
    # app.json_encoder = TernJSONEncoder

    ################################################################
    # Configure application
    ################################################################
    # load defaults
    from duma_backend import settings

    load_settings(app, env_prefix="DUMA_BACKEND_", defaults=settings, config=config)

    ################################################################
    # Configure logging
    ################################################################
    app_logging.init_app(app)

    #################################################################
    # Configure various Flask extensions used by this app
    #################################################################
    from flask_tern import cache

    cache.init_app(app)

    #################################################################
    # Configure sqlalchemy ad alembic
    #################################################################
    # Register extensions
    from flask_tern import db

    # api.init_app(app)
    db.init_app(app)
    Migrate(app, db.db, directory=os.path.join(app.config.root_path, "migrations"))

    ###############################################
    # Session setup
    ###############################################
    if app.config.get("SESSION_TYPE"):
        # only configure Flask-Session if requested, fall back to falsk Secure Cookie Session.
        from flask_session import Session

        Session(app)

    #################################################################
    # Configure elasticsearch
    #################################################################
    from flask_tern import elasticsearch

    elasticsearch.init_app(app)

    ###############################################
    # CORS
    ###############################################
    # TODO: there is more to this
    CORS(app)

    ###############################################
    # ProxyFix
    ###############################################
    # x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    ###############################################
    # Healthcheck
    ###############################################
    from flask_tern import healthcheck

    # TODO: add authorization to /metrics endpoint
    healthcheck.init_app(app)
    # app.extensions["healthcheck"].add_check(healthcheck.check_db)
    # app.extensions["healthcheck"].add_check(healthcheck.check_keycloak)

    #############################################
    # Setup OIDC
    #############################################
    from flask_tern import auth

    auth.init_app(app)

    ##############################################
    # Register routes and views
    ##############################################
    # register oidc session login blueprints
    from flask_tern.auth.login import oidc_login

    app.register_blueprint(oidc_login, url_prefix="/api/oidc")

    # register api blueprints
    from duma_backend.views import api_v1, home

    app.register_blueprint(home.bp, url_prefix="/api")
    app.register_blueprint(api_v1.bp, url_prefix="/api/v1.0")

    # setup build_only route so that we can use url_for("root", _external=True) - "root" route required by oidc session login
    # app.add_url_rule("/", "root", build_only=True)
    app.add_url_rule(
        "/", "root", view_func=lambda: redirect(url_for("home.home", _external=True))
    )
    return app
