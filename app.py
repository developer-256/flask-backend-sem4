#  pip freeze > requirements.txt
#  flask --app app.py --debug run

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import uuid
from functools import wraps
import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mssql+pyodbc://SA:YourStrong!Passw0rd@localhost/Project?driver=ODBC+Driver+17+for+SQL+Server"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def generate_uuid_key():
    return str(uuid.uuid4())


def AddKeysToTable(keys, table):
    return [dict(zip(keys, row)) for row in table]


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


@app.route("/")
def hello_world():
    return {"Project Name": "University Database and Python Project"}


@app.route("/register", methods=["POST"])
def register():
    fname = request.form.get("fname")  # Use form data for POST requests
    lname = request.form.get("lname")
    uname = request.form.get("uname")
    email = request.form.get("email")
    password = request.form.get("password")

    if not all([fname, lname, email, uname, password]):
        return (
            jsonify(
                {
                    "error": "Invalid Data. Please provide valid values for all fields.",
                    "data": {
                        "fname": fname,
                        "lname": lname,
                        "uname": uname,
                        "email": email,
                        "password": password,
                    },
                }
            ),
            400,
        )
    try:
        # check if email is unique
        user = db.session.execute(
            text("Select Email FROM USERS WHERE Email = :email"), {"email": email}
        ).fetchone()
        if user is not None:
            return jsonify({"error": "User already registered. Sign in Instead"}), 400

        # check if email is unique
        username = db.session.execute(
            text("Select * FROM USERS WHERE UserName = :uname"), {"uname": uname}
        ).fetchone()

        if username is not None:
            return jsonify({"error": "Username already taken"}), 400

        now = datetime.datetime.now()
        print("date1: ", now)
        db.session.execute(
            text(
                "INSERT INTO USERS (FirstName, LastName, UserName, Email, UserPassword, createdAt, updatedAt) VALUES (:FirstName, :LastName, :UserName, :Email, :UserPassword, :createdAt, :updatedAt)",
            ),
            {
                "FirstName": fname,
                "LastName": lname,
                "UserName": uname,
                "Email": email,
                "UserPassword": password,
                "createdAt": now,
                "updatedAt": now,
            },
        )
        db.session.commit()
        new_user = db.session.execute(
            text(
                "SELECT FirstName, LastName, Email FROM USERS WHERE Email = :email",
            ),
            {"email": email},
        ).fetchone()
        columns = ["FirstName", "LastName", "Email"]
        user_data = dict(zip(columns, new_user))
        return user_data

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/signin", methods=["POST"])
def signin():
    email = request.form.get("email")
    password = request.form.get("password")

    if not all([email, password]):
        return (
            jsonify(
                {
                    "error": "Invalid Data. Please provide valid values for all fields.",
                    "data": {"email": email, "password": password},
                }
            ),
            400,
        )

    try:
        user = db.session.execute(
            text(
                "SELECT Email, UserPassword, SessionToken FROM USERS WHERE Email = :email",
            ),
            {"email": email},
        ).fetchone()

        if user is None:
            return jsonify({"error": "User does not exist. Register instead"}), 400

        # if user.UserPin != password:
        if user[1] != password:
            return jsonify({"error": "Invalid Password"}), 400

        if user[2] is None:
            # if user.sessionToken is None:
            db.session.execute(
                text(
                    "UPDATE USERS SET SessionToken=:sessionToken WHERE email = :email",
                ),
                {"sessionToken": generate_uuid_key(), "email": email},
            )
            db.session.commit()

        user = db.session.execute(
            text(
                "SELECT FirstName, LastName, Email, SessionToken FROM USERS WHERE Email = :email",
            ),
            {"email": email},
        ).fetchone()
        columns = ["FirstName", "LastName", "Email", "Session_Token"]
        user_data = dict(zip(columns, user))
        return user_data

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization").split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing!"}), 401

        try:
            user = db.session.execute(
                text("SELECT Email FROM Users WHERE sessionToken = :token"),
                {"token": token},
            ).fetchone()
            if user is None:
                return jsonify({"error": "Invalid or expired token!"}), 401

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return f(*args, **kwargs)

    return decorated


@app.route("/users")
@token_required
def get_users():

    token = request.headers.get("Authorization").split(" ")[1]
    print("3.", token)

    try:
        table = db.session.execute(text("SELECT * FROM Users")).fetchall()
        columns = [
            "UserID",
            "FirstName",
            "LastName",
            "Email",
            "UserPin",
            "Session_Token",
        ]
        tableWithKeys = AddKeysToTable(columns, table)

        return jsonify(tableWithKeys)
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
