import pymongo, os
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "nbyula nithin"
database_name = "jobify"
mongo_uri = os.getenv("MONGO_URI")


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("listings"))
    else:
        return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form["email"]
        password = request.form["password"]

        client = pymongo.MongoClient(mongo_uri)
        db = client[database_name]
        collection = db["auth"]

        user = collection.find_one({"email": email, "password": password})

        if user is None:
            flash("Invalid credentials!", "danger")
            return redirect(url_for("login"))

        session["user"] = user
        return redirect(url_for("listings"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        user_type = request.form["user-type"]

        client = pymongo.MongoClient(mongo_uri)
        db = client[database_name]
        collection = db["auth"]

        if collection.find_one({"email": email}) is not None:
            flash("Email already exists!", "danger")
            return redirect(url_for("signup"))

        collection.insert_one(
            {"name": name, "type": user_type, "email": email, "password": password}
        )
        flash("Account created successfully!", "success")
        return redirect(url_for("login"))


@app.route("/listings")
def listings():
    if "user" in session:
        if session["user"].get("type") == "terraformer":
            return redirect(url_for("listings_admin"))
        else:
            client = pymongo.MongoClient(mongo_uri)
            db = client[database_name]
            collection = db["jobs"]

            jobs = collection.find({})

            return render_template("listings.html", jobs=jobs)
    else:
        return redirect(url_for("home"))


@app.route("/listings_admin")
def listings_admin():
    if "user" in session:
        if session["user"].get("type") == "terraformer":
            client = pymongo.MongoClient(mongo_uri)
            db = client[database_name]
            collection = db["jobs"]

            jobs = collection.find({})

            return render_template("listings_admin.html", jobs=jobs)
        else:
            return redirect(url_for("listings"))
    else:
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
