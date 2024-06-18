from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

# MongoDB Setup
url = os.environ.get("url")

client = MongoClient(url, server_api=ServerApi("1"))
# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# WSGI Application
app = Flask(__name__)


@app.route("/", methods=["GET"])
def homePage():
    return render_template("home.html")


@app.route("/register", methods=["POST", "GET"])
def registrationPage():
    if request.method == "POST":
        user = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        client.loginPageCluster.customer.insert_one(
            {"username": user, "email": email, "password": password}
        )
        print(f"Registered user: {user}, email: {email}")
        return redirect(url_for("loginPage"))

    return render_template("registration.html")


@app.route("/login", methods=["POST", "GET"])
def loginPage():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]
        print(f"Login attempt for user: {user}")
        result = client.loginPageCluster.customer.find_one(
            {"username": user, "password": password}
        )
        if result:
            return redirect(url_for("credentials", username=user))
        else:
            return "Invalid Username or Password", 401

    return render_template("login.html")


@app.route("/credentials/<username>", methods=["GET"])
def credentials(username):
    print(f"Fetching credentials for user: {username}")
    user_info = client.loginPageCluster.customer.find_one({"username": username})
    if user_info:
        print(f"User info: {user_info}")
        return render_template(
            "credentials.html",
            username=user_info["username"],
            email=user_info["email"],
            password=user_info["password"],
        )
    else:
        print("User not found")
        return "User not found", 404

if __name__ == "__main__":
    app.run(debug=True)