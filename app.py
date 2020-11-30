import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_tasks")
def get_tasks():
    tasks = list(mongo.db.recipe.find())
    return render_template("tasks.html", tasks=tasks)

@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    tasks = list(mongo.db.recipe.find({"$text":{"$search": query}}))
    return render_template("tasks.html", tasks=tasks)

@app.route("/search_categories", methods=["GET", "POST"])
def search_categories():
    query = request.form.get("query")
    categories = list(mongo.db.categories.find({"$text":{"$search": query}}).sort("category_name", 1))
    return render_template("categories.html", categories=categories)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()})
            if existing_user:
                flash("Username Already Exists")
                return redirect(url_for("register"))

            existing_user = mongo.db.users.find_one(
                {"email": request.form.get("email").lower()})
            if existing_user:
                flash("E-mail Already Exists")
                return redirect(url_for("register"))

            register = {
                "username": request.form.get("username").lower(),
                "email": request.form.get("email").lower(),
                "password": generate_password_hash(request.form.get("password"))
            }
            mongo.db.users.insert_one(register)

            session["user"] = request.form.get("username").lower()
            flash("Registration Successful")
            return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("welcome, {}".format(request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You have been logged out, See you again !")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        task = {
            "category_name": request.form.get("category_name"),
            "type_of_food": request.form.get("type_of_food"),
            "recipe_name": request.form.get("recipe_name"),
            "recipe_description": request.form.get("recipe_description"),
            "recipe_ingredient": request.form.get("recipe_ingredient"),
            "recipe_directions": request.form.get("recipe_directions"),
            "recipe_image": request.form.get("image_display"),
            "created_by": session["user"]
        }
        mongo.db.recipe.insert_one(task)
        flash("Recipe Successfully Added")
        return redirect(url_for("get_tasks"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "type_of_food": request.form.get("type_of_food"),
            "recipe_name": request.form.get("recipe_name"),
            "recipe_description": request.form.get("recipe_description"),
            "recipe_ingredient": request.form.get("recipe_ingredient"),
            "recipe_directions": request.form.get("recipe_directions"),
            "recipe_image": request.form.get("image_display"),
            "created_by": session["user"]
        }
        mongo.db.recipe.update({"_id": ObjectId(task_id)}, submit)
        flash("Recipe Successfully Updated")
        return redirect(url_for("get_tasks"))

    task = mongo.db.recipe.find_one({"_id": ObjectId(task_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_recipe.html", task=task, categories=categories)


@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    mongo.db.recipe.remove({"_id": ObjectId(task_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("get_tasks"))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))
        
    return render_template("add_category.html")

@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)

@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)