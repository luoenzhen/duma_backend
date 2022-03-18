from . import db


class Example(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False)
