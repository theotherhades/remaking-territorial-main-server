# refer to this for password hashing with bcrypt: https://stackoverflow.com/questions/9594125/salt-and-hash-a-password-in-python
import uuid
import json
import flask
import bcrypt
import config
from pymongo import MongoClient

app = flask.Flask(__name__)
cluster = MongoClient(config.db_url)
db = cluster["test"]
usercol = db["users"]


@app.route("/", methods = ["GET"])
def index():
    return "Hello, world!"

@app.route("/register_user", methods = ["POST"])
def register_user():
    """
    Registers a new user account.
    Headers:
    - username: The new user's username. Max length 20 chars.
    - pswd: The new user's password.
    - quote: A short bit of descriptive text, max length 280 chars.
    """
    username = flask.request.headers.get("username")
    pswd = flask.request.headers.get("pswd")
    quote = flask.request.headers.get("quote")
    newid = uuid.uuid4().hex

    if len(username) > 20:
        return json.dumps({"error": True, "content": f"Username too long; limit is 20 chars: {username}"})
    elif len(quote) > 280:
        return json.dumps({"error": True, "content": f"Quote too long; limit is 280 chars: {quote}"})
    else:
        usercol.insert_one({"_id": newid, "username": str(username), "pswd": bcrypt.hashpw(pswd.encode("utf-8"), bcrypt.gensalt()), "quote": quote})
        return json.dumps({"error": False, "content": f"Successfully created user {username}. ID: {newid}"})

@app.route("/user", methods = ["GET"])
def user():
    """
    Returns a user's data as stringified JSON.
    URL Parameters:
    - id: The ID for the user to get data for.
    """
    userid = flask.request.args.get("id")
    if usercol.count_documents({"_id": userid}, limit = 1):
        data = usercol.find_one({"_id": userid})
        return json.dumps({"error": False, "content": {"_id": data["_id"], "username": data["username"], "quote": data["quote"]}})
    else:
        return json.dumps({"error": True, "content": f"No user exists with ID {userid}"})
    
@app.route("/userlist", methods = ["GET"])
def userlist():
    """
    Returns all registered usernames and their corresponding ids.
    """
    userlist = {}
    for user in usercol.find():
        if user["_id"] == "placeholder":
            continue
        userlist[user["username"]] = user["_id"]

    return json.dumps(userlist)


app.run("0.0.0.0")