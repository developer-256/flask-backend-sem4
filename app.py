#  pip freeze > requirements.txt
#  flask --app app.py --debug run

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import uuid
from functools import wraps
import datetime
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

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
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Session token is missing!"}), 401

        token = token.split(" ")[1]
        # print(f"001: Session Token: -{token}")

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
    title = request.json.get("title")
    content = request.json.get("content")
    tags = request.json.get("tags")
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

        # Get the QuesID of the newly inserted question using SCOPE_IDENTITY()
        QuesID = db.session.execute(
            text("SELECT TOP 1 QuesID FROM QUESTIONS ORDER BY QuesID DESC")
        ).fetchone()
        if tags:
            for tag in tags:
                existing_tag = db.session.execute(
                    text("SELECT QTagID FROM QTAG WHERE Tag = :tag"),
                    {"tag": tag},
                ).fetchone()

                if not existing_tag:
                    db.session.execute(
                        text("INSERT INTO QTAG (Tag) VALUES (:tag)"),
                        {"tag": tag},
                    )
                    db.session.commit()
                    qtagID = db.session.execute(
                        text("SELECT TOP 1 QTagID FROM QTAG ORDER BY QTagID DESC")
                    ).fetchone()
                else:
                    qtagID = existing_tag

                # Insert into the Question_QTAG table to link the question and the tag
                db.session.execute(
                    text(
                        "INSERT INTO Question_QTAG (QuesID, QTagID) VALUES (:quesID, :qtagID)"
                    ),
                    {"quesID": QuesID[0], "qtagID": qtagID[0]},
                )
                db.session.commit()

        question = db.session.execute(
            text(
                "SELECT TOP 1 QuesID, Title, Content, createdAt FROM QUESTIONS WHERE UserID = :userID ORDER BY createdAt DESC"
            ),
            {"userID": userID[0]},
        ).fetchone()

        columns = ["QuesID", "Title", "Content", "createdAt"]
        response = dict(zip(columns, question))

        # print(response)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/getquestions")
def getQuestion():
    # query = request.args.get("query")
    sort = request.args.get("sort")

    try:
        dbQuery = "SELECT QUESTIONS.QuesID, QUESTIONS.UserID, USERS.UserName, QUESTIONS.Title, QUESTIONS.Content, QUESTIONS.likes, QUESTIONS.updatedAt, STUFF(( SELECT ', ' + QTAG.Tag FROM QTAG INNER JOIN Question_QTAG ON Question_QTAG.QTagID = QTAG.QTagID WHERE Question_QTAG.QuesID = QUESTIONS.QuesID FOR XML PATH('') ), 1, 1, '') AS Tags FROM QUESTIONS INNER JOIN USERS ON QUESTIONS.UserID = USERS.UserID ORDER BY QUESTIONS.updatedAt DESC;"

        if sort == "desc":
            dbQuery = "SELECT QUESTIONS.QuesID, QUESTIONS.UserID, USERS.UserName, QUESTIONS.Title, QUESTIONS.Content, QUESTIONS.likes, QUESTIONS.updatedAt, STUFF(( SELECT ', ' + QTAG.Tag FROM QTAG INNER JOIN Question_QTAG ON Question_QTAG.QTagID = QTAG.QTagID WHERE Question_QTAG.QuesID = QUESTIONS.QuesID FOR XML PATH('') ), 1, 1, '') AS Tags FROM QUESTIONS INNER JOIN USERS ON QUESTIONS.UserID = USERS.UserID ORDER BY QUESTIONS.updatedAt;"

        table = db.session.execute(text(dbQuery)).fetchall()
        columns = [
            "QuesID",
            "UserID",
            "UserName",
            "Title",
            "Content",
            "likes",
            "updatedAt",
            "Tags",
        ]
        response = [dict(zip(columns, rows)) for rows in table]
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @app.route("/like-question")
# @token_required
# def likeQuestion():
#     QuesID = request.args.get("QuesID")
#     QuesID = int(QuesID)
#     # token = request.headers.get("Authorization").split(" ")[1]
#     try:
#         db.session.execute(text("UPDATE QUESTIONS SET likes"))
#         return {"kfjl": "lkjasdf"}
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


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

        if question is None:
            return jsonify({"error": "Question not found"}), 404

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
    title = request.json.get("title")
    content = request.json.get("content")

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
            return (
                jsonify({"error": "Question does not belong to you"}),
                404,
            )

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


@app.route("/delete-question", methods=["POST"])
@token_required
def deleteQuestion():
    QuesID = request.args.get("QuesID")
    token = request.headers.get("Authorization").split(" ")[1]

    try:
        UserID = db.session.execute(
            text("SELECT UserID FROM USERS WHERE SessionToken = :token"),
            {"token": token},
        ).fetchone()

        isUserQues = db.session.execute(
            text(
                "SELECT QuesID, UserID, Title, Content FROM QUESTIONS WHERE QuesID = :QuesID AND UserID = :UserID"
            ),
            {"QuesID": QuesID, "UserID": UserID[0]},
        ).fetchone()

        if isUserQues is None:
            return (
                jsonify({"error": "Question not found or doesn't belong to you"}),
                404,
            )

        db.session.execute(
            text("DELETE FROM QUESTIONS WHERE QuesID = :QuesID AND UserID = :UserID"),
            {"QuesID": QuesID, "UserID": UserID[0]},
        )
        db.session.commit()

        columns = ["QuesID", "UserID", "Title", "Content"]
        response = dict(zip(columns, isUserQues))

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/create-answer", methods=["POST"])
@token_required
def createAnswer():
    QuesID = request.form.get("QuesID")
    Content = request.form.get("Content")
    token = request.headers.get("Authorization").split(" ")[1]

    try:
        User = db.session.execute(
            text("SELECT UserID FROM USERS WHERE SessionToken = :token"),
            {"token": token},
        ).fetchone()

        QuesExist = db.session.execute(
            text("SELECT QuesID FROM QUESTIONS WHERE QuesID = :QuesID"),
            {"QuesID": QuesID},
        ).fetchone()

        if QuesExist is None:
            return jsonify({"error": "Question does not exist"}), 404

        db.session.execute(
            text(
                "INSERT INTO ANSWERS(content, upvotes, downvotes, UserID, QuesID) VALUES (:content, :upvotes, :downvotes, :userID, :QuesID)"
            ),
            {
                "content": Content,
                "upvotes": 0,
                "downvotes": 0,
                "userID": User[0],
                "QuesID": QuesID,
            },
        )
        db.session.commit()

        print(
            f"Inserting Answer: UserID = {User[0]}, QuesID = {QuesID}, Content = {Content}"
        )

        Answer = db.session.execute(
            text(
                "SELECT TOP 1 * FROM ANSWERS WHERE UserID = :UserID AND QuesID = :QuesID ORDER BY AnsID DESC"
            ),
            {"UserID": User[0], "QuesID": QuesID},
        ).fetchone()

        columns = ["AnsID", "Content", "UserID", "QuesID"]

        Response = dict(zip(columns, Answer))

        return jsonify(Response)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/get-user")
@token_required
def getUser():
    token = request.headers.get("Authorization").split(" ")[1]
    try:
        User = db.session.execute(
            text(
                "SELECT UserID, FirstName, LastName, UserName, Email, Bio, createdAt FROM USERS WHERE SessionToken = :token"
            ),
            {"token": token},
        ).fetchone()

        columns = [
            "UserID",
            "FirstName",
            "LastName",
            "UserName",
            "Email",
            "Bio",
            "createdAt",
        ]

        response = dict(zip(columns, User))

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
