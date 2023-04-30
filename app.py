import pymongo, os
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "nbyula nithin"
database_name = "jobify"
mongo_uri = os.getenv("MONGO_URI")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(debug=True)
