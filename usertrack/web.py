import re
from os import environ
from flask import Flask, render_template, request, session, flash, redirect, url_for, abort
from email_validator import validate_email, EmailNotValidError
from .models import db_session, User, Post

app = application = Flask(__name__)

app.secret_key = environ["SECRET_KEY"]

def check_login(s, email, clearpass):
    user = s.query(User).filter(email==User.email).first()
    if user and user.has_password(clearpass):
        return user

@app.route("/", methods=["GET"])
def get_index():
    with db_session() as s:
        poster = user = check_login(s, session.get("email", ""), session.get("clearpass", ""))
        if user:
            posts = s.query(Post).order_by(Post.ctime.desc()).all()
            return render_template("index.html", **locals())
        else:
            return redirect(url_for("get_login"))

@app.route("/user/<email>", methods=["GET"])
def get_user(email):
    with db_session() as s:
        poster = check_login(s, session.get("email", ""), session.get("clearpass", ""))
        user = s.query(User).filter(email==User.email).first()
        if user:
            return render_template("sent.html", **locals())
        else:
            abort(404)

@app.route("/user/<email>", methods=["POST"])
def post_user(email):
    with db_session() as s:
        poster = check_login(s, session.get("email", ""), session.get("clearpass", ""))
        user = s.query(User).filter(email==User.email).first()
        valid = True
        if "title" in request.form:
            title = request.form["title"]
            if len(title) == 0:
                flash("Invalid Title")
                valid = False
        else:
            flash("Invalid Title")
            valid = False
        if "contents" in request.form:
            contents = request.form["contents"]
            if len(contents) == 0:
                flash("Invalid Contents")
                valid = False
        else:
            flash("Invalid Contents")
            valid = False
        if poster and user and valid:
            post = Post(from_user_id=poster.id, title=title, contents=contents)
            s.add(post)
        return redirect(url_for("get_user", email=email))



@app.route("/login", methods=["GET"])
def get_login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def post_login():
    valid = True
    try:
        email = validate_email(request.form["email"])["email"]
    except (KeyError, EmailNotValidError):
        flash("Invalid Email.")
        valid = False
    try:
        clearpass = request.form["password"]
    except KeyError:
        flash("No Password.")
        valid = False
    if not valid:
        return redirect(url_for("get_login"))
    with db_session() as s:
        user = check_login(s, email, clearpass)
        if user:
            session["email"] = email
            session["clearpass"] = clearpass
    return redirect(url_for("get_index"))

@app.route("/logout", methods=["POST"])
def post_logout():
    session.clear()
    return redirect(url_for("get_index"))

LETTERS = re.compile("^[-a-zA-Z]+$")

@app.route("/register", methods=["GET"])
def get_register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def post_register():
    valid = True
    try:
        email = validate_email(request.form["email"])["email"]
    except (KeyError, EmailNotValidError):
        flash("Invalid Email.")
        valid = False
    try:
        first_name = request.form["first_name"]
        if not LETTERS.match(first_name):
            flash("Invalid First Name.")
            valid = False
    except KeyErorr:
        flash("Invalid First Name.")
        valid = False
    try:
        last_name = request.form["last_name"]
        if not LETTERS.match(last_name):
            flash("Invalid Last Name.")
            valid = False
    except KeyErorr:
        flash("Invalid Last Name.")
        valid = False

    try:
        clearpass = request.form["password"]
        clearpass2 = request.form["confirm_password"]
        if clearpass != clearpass2:
            flash("Passwords do not match.")
            valid = False
        if len(clearpass) < 8:
            flash("Password is too short.")
            valid = False
    except KeyError:
        flash("No Password.")
        valid = False
    if not valid:
        return redirect(url_for("get_register"))
    with db_session() as s:
        user = User(email=email, first_name=first_name, last_name=last_name)
        user.set_password(clearpass)
        s.add(user)
    return redirect(url_for("get_index"))

