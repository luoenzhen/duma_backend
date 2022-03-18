from flask import Blueprint, jsonify, redirect, url_for
from flask_tern.auth import current_user, require_user

bp = Blueprint("home", __name__)


@bp.route("/")
def home():
    """Redirect to default API root.

    The default API is a OpenAPIBlueprint and will redirect to the included swagger UI.
    """
    return redirect(url_for("api_v1.api_root", _external=True))


@bp.route("/whoami")
@require_user
def whoami():
    """Check login status and return user info if authenticated."""
    return jsonify(current_user._get_current_object())
