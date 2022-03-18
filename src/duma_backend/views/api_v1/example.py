from flask import jsonify
from flask_tern import openapi
from flask_tern.auth import current_user, require_user
from flask_tern.logging import create_audit_event, log_audit
from duma_backend.models import Example, db

from .blueprint import bp


@bp.route("/example")
@openapi.validate()
def example_get():
    log_audit(create_audit_event("increment", "success"))
    counter = db.session.query(Example).first()
    if not counter:
        counter = Example(count=0)
        db.session.add(counter)
    counter.count += 1
    db.session.commit()
    return jsonify({"counter": counter.count})


@bp.route("/example/<name>", methods=["POST"])
@require_user
@openapi.validate()
def hello_post(name):
    counter = db.session.query(Example).first()
    return jsonify(
        {
            "name": name,
            "counter": counter.count,
            "current_user": current_user._get_current_object(),
        }
    )
