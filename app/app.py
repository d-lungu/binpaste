import os
import datetime
import string
import time
import flask
import pymongo
import bson
import random

app = flask.Flask(__name__)
PASTE_ID_LENGTH = 20


def get_db() -> pymongo.MongoClient:
    db = getattr(flask.g, "_database", None)

    if db is None:
        db = flask.g._database = pymongo.MongoClient(
            get_config()["MONGO_URL"]
        ).dennylungu

    return db


def generate_paste_id() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=PASTE_ID_LENGTH))


@app.errorhandler(400)
def resource_not_found(e):
    return flask.jsonify(error=str(e)), 400


def get_config() -> dict:
    config = getattr(flask.g, "_config", None)

    if config is None:
        from dotenv import dotenv_values

        config = dotenv_values(".env")

    return config


@app.route("/")
def index() -> str:
    return flask.render_template("index.html")


@app.route("/<string:paste_id>")
def paste(paste_id: str) -> str:
    paste_data = get_db().pastes.find_one({"id": paste_id})

    return flask.render_template("paste.html", PASTE_DATA=paste_data["text"])


@app.route("/api/upload", methods=["POST"])
def upload():
    paste_text = flask.request.json["text"]

    if not paste_text:
        flask.abort(400, description="No text provided")

    # check for possible collisions
    while True:
        paste_id = generate_paste_id()
        res = get_db().pastes.find_one({"id": paste_id})

        if res is None:
            break

    get_db().pastes.insert_one({"id": paste_id, "text": paste_text})

    return flask.jsonify({"paste_id": paste_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0")
