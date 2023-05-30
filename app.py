import pymongo, os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from bson import json_util
import json
import datetime
import secrets

app = Flask(__name__)
app.config["SECRET_KEY"] = "nbyula nithin"
database_name = "jobify"

# loading env data
try:
	from dotenv import load_dotenv

	load_dotenv()
except Exception as err:
	print(err)

mongo_uri = os.getenv("MONGO_URI")
print(mongo_uri)

@app.route("/")
def home():
	if "user" in session:
		return redirect(url_for("listings"))
	else:
		return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
	if "user" in session:
		return redirect(url_for("listings"))
	else:
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

			session["user"] = json.loads(json_util.dumps(user))
			return redirect(url_for("listings"))


@app.route("/logout")
def logout():
	session.pop("user", None)
	return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
	if "user" in session:
		return redirect(url_for("listings"))
	else:
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

			collection.insert_one({
			 "name": name,
			 "type": user_type,
			 "email": email,
			 "password": password
			})
			flash("Account created successfully!", "success")
			return redirect(url_for("login"))


@app.route("/listings", methods=["GET", "POST"])
def listings():
	if "user" in session:
		if session["user"].get("type") == "terraformer":
			return redirect(url_for("listings_admin"))
		else:
			return render_template("listings.html")
	else:
		return redirect(url_for("home"))


@app.route("/id/<id>")
def listings_reg(id):
	if "user" in session:
		if session["user"].get("type") == "terraformer":
			return redirect(url_for("listings_admin"))
		else:
			client = pymongo.MongoClient(mongo_uri)
			db = client[database_name]
			collection = db["jobs"]

			collection.update_one(
			 {"id": id}, {"$addToSet": {
			  "interested": session["user"]["email"]
			 }})

			job_name = collection.find_one({"id": id}, {"_id": 0, "title": 1})["title"]

			flash(f"You have successfully registered for {job_name} Job!", "success")
			return redirect(url_for("listings"))
	else:
		return redirect(url_for("home"))


@app.route("/listings_admin", methods=["GET", "POST"])
def listings_admin():
	if "user" in session:
		if session["user"].get("type") == "terraformer":
			if request.method == "GET":
				return render_template("listings_admin.html")
			else:
				return json.loads(json_util.dumps(request.form))
		else:
			return redirect(url_for("listings"))
	else:
		return redirect(url_for("home"))


@app.route("/listings_admin/add", methods=["GET", "POST"])
def add_listing():
	if "user" in session:
		if session["user"].get("type") == "terraformer":
			if request.method == "GET":
				current_time = datetime.datetime.now()
				form_id = secrets.token_hex(8)
				return render_template("add_listing.html",
				                       current_time=current_time,
				                       form_id=form_id)
			else:
				client = pymongo.MongoClient(mongo_uri)
				db = client[database_name]
				collection = db["jobs"]

				job = {
				 "id": request.form["id"],
				 "title": request.form["title"],
				 "description": request.form["markdown"],
				 "location": request.form["location"],
				 "deadline": request.form["deadline"],
				 "email": request.form["email"],
				 "phone": request.form["phone"],
				 "archived": False,
				 "interested": [],
				 "position": 1,
				}

				collection.insert_one(job)
				flash("Job added successfully!", "success")
				return redirect(url_for("add_listing"))
		else:
			return redirect(url_for("listings"))
	else:
		return redirect(url_for("home"))


@app.route("/listings/json")
def listings_json():
	client = pymongo.MongoClient(mongo_uri)
	db = client[database_name]
	collection = db["jobs"]

	jobs = collection.find({"archived": False}, {
	 "_id": 0,
	 "interested": 0,
	 "archived": 0
	})
	return json_util.dumps(jobs)


@app.route("/listings/all")
def listings_all():
	if "user" in session:
		if session["user"].get("type") == "terraformer":
			client = pymongo.MongoClient(mongo_uri)
			db = client[database_name]
			collection = db["jobs"]

			jobs = collection.find({})
			return json_util.dumps(jobs)
		else:
			return []
	else:
		return []


@app.errorhandler(404)
def not_found_error(error):
	return redirect(url_for("home"))


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)
