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


@app.route("/test")
def test():
    try:
        test = db.session.execute(
            text("SELECT * FROM QUESTIONS Where UserID = 1")
        ).fetchall()

        columns = [
            "QuesID",
            "Title",
            "Content",
            "createdAt",
            "updatedAt",
            "UserID",
        ]

        table = AddKeysToTable(columns, test)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify(table)


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


@app.route("/postquestion", methods=["POST"])
@token_required
def postquestion():
    title = request.form.get("title")
    content = request.form.get("content")
    token = request.headers.get("Authorization").split(" ")[1]

    try:
        userID = db.session.execute(
            text("SELECT UserID FROM USERS WHERE SessionToken = :token"),
            {"token": token},
        ).fetchone()

        date = datetime.datetime.now()
        db.session.execute(
            text(
                "INSERT INTO QUESTIONS(Title, Content, UserID, createdAt, updatedAt) VALUES (:title, :content, :userID, :createdAt, :updatedAt)"
            ),
            {
                "title": title,
                "content": content,
                "userID": userID[0],
                "createdAt": date,
                "updatedAt": date,
            },
        )
        db.session.commit()

        table = db.session.execute(
            text(
                "SELECT QuesID, Title, Content, createdAt FROM QUESTIONS WHERE UserID = :userID ORDER BY createdAt DESC"
            ),
            {"userID": userID[0]},
        ).fetchall()

        columns = ["QuesID", "Title", "Content", "createdAt"]
        response = [dict(zip(columns, rows)) for rows in table]

        print(response[0])
        return jsonify(response[0])
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/getquestions")
def getQuestion():
    # query = request.args.get("query")
    sort = request.args.get("sort")

    try:
        dbQuery = "SELECT * FROM QUESTIONS"

        if sort == "desc":
            dbQuery = "SELECT * FROM QUESTIONS ORDER BY createdAt DESC"

        table = db.session.execute(text(dbQuery)).fetchall()
        columns = [
            "QuesID",
            "Title",
            "Content",
            "createdAt",
            "UserID",
        ]
        response = [dict(zip(columns, rows)) for rows in table]
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get-user-questions")
@token_required
def getUserQuestions():
    token = request.headers.get("Authorization").split(" ")[1]

    try:
        UserID = db.session.execute(
            text("SELECT UserID FROM USERS WHERE SessionToken = :token"),
            {"token": token},
        ).fetchone()

        table = db.session.execute(
            text("SELECT * FROM QUESTIONS WHERE UserID = :UserID"),
            {"UserID": UserID[0]},
        ).fetchall()

        columns = [
            "QuesID",
            "Title",
            "Content",
            "createdAt",
            "updatedAt",
            "UserID",
        ]
        response = [dict(zip(columns, rows)) for rows in table]

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get-question-by-id")
def getQuesByID():
    QuesID = request.args.get("QuesID")

    try:
        question = db.session.execute(
            text("SELECT * FROM QUESTIONS WHERE QuesID = :QuesID"), {"QuesID": QuesID}
        ).fetchone()

        columns = [
            "QuesID",
            "Title",
            "Content",
            "createdAt",
            "updatedAt",
            "UserID",
        ]

        response = dict(zip(columns, question))

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/editquestion", methods=["POST"])
@token_required
def editQuestion():
    QuesID = request.args.get("QuesID")
    token = request.headers.get("Authorization").split(" ")[1]
    title = request.form.get("title")
    content = request.form.get("content")

    try:
        user = db.session.execute(
            text("SELECT UserID FROM USERS WHERE SessionToken = :token"),
            {"token": token},
        ).fetchone()

        isUserQuestion = db.session.execute(
            text(
                "SELECT QuesID FROM QUESTIONS WHERE UserID = :user AND QuesID = :QuesID"
            ),
            {"user": user[0], "QuesID": QuesID},
        ).fetchone()

        if isUserQuestion is None:
            return jsonify({"error": "Question not Found"}), 404

        updatedAt = datetime.datetime.now()
        db.session.execute(
            text(
                "UPDATE QUESTIONS SET title = :title, content = :content, updatedAt = :updatedAt WHERE QuesID = :QuesID"
            ),
            {
                "title": title,
                "content": content,
                "updatedAt": updatedAt,
                "QuesID": QuesID,
            },
        )
        db.session.commit()

        question = db.session.execute(
            text("SELECT * FROM QUESTIONS WHERE QuesID = :QuesID"),
            {"QuesID": QuesID},
        ).fetchone()

        columns = [
            "QuesID",
            "Title",
            "Content",
            "createdAt",
            "updatedAt",
            "UserID",
        ]
        response = dict(zip(columns, question))
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
