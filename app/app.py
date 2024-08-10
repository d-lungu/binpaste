import string
import flask
import pymongo
import random
import redis
import flask_caching
import flask_limiter

REDIS_HOST = "localhost"
REDIS_PORT = 6379

app = flask.Flask(__name__)
app.config.from_mapping(
    {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": redis.Redis(host=REDIS_HOST, port=REDIS_PORT),
        "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 24 * 30  # 1 month
    }
)
cache = flask_caching.Cache(app)
PASTE_ID_LENGTH = 20
limiter = flask_limiter.Limiter(
    flask_limiter.util.get_remote_address,
    app=app,
    default_limits=["10 per second", "100 per minute", "250 per hour", "500 per day"],
    # Redis
    storage_uri="redis://localhost:6379",
    strategy="fixed-window",  # or "moving-window"
)


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


@app.errorhandler(429)
def resource_not_found(e):
    return flask.jsonify(error="429 Too Many Requests"), 429


def get_config() -> dict:
    config = getattr(flask.g, "_config", None)

    if config is None:
        from dotenv import dotenv_values

        config = dotenv_values(".env")

    return config


@app.route("/", methods=["GET"])
@cache.cached()
def index() -> str:
    return flask.render_template("index.html")


@app.route("/<string:paste_id>", methods=["GET"])
@cache.cached()
def paste(paste_id: str) -> str:
    paste_data = get_db().pastes.find_one({"id": paste_id})

    if not paste_data:
        flask.abort(400, description=f"No paste with id {paste_id} found")

    paste_troncated = paste_data["text"]
    if len(paste_troncated) > 256:
        paste_troncated = paste_troncated[:256]

    return flask.render_template("paste.html", PASTE_DATA=paste_data["text"], EMBED_DESCRIPTION=paste_troncated)


@app.route("/api/upload", methods=["POST"])
def upload():
    paste_text = flask.request.json["text"]

    if not paste_text:
        flask.abort(400, description="No text provided")

    """
    removed as the chances of a collision happening are miniscule. Should the paste ids be based on the timestamp?
    # check for possible collisions
    while True:
        paste_id = generate_paste_id()
        res = get_db().pastes.find_one({"id": paste_id})

        if res is None:
            break
    """

    paste_id = generate_paste_id()
    get_db().pastes.insert_one({"id": paste_id, "text": paste_text})

    return flask.jsonify({"paste_id": paste_id})


if __name__ == "__main__":
    app.run(host="0.0.0.0")
