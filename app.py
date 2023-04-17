import pymongo
from bson import ObjectId
from flask import Flask, render_template, request, url_for, redirect, session
import bcrypt

# from todo.todo import todo_bp

app = Flask(__name__)
app.secret_key = "testing"
# app.register_blueprint(todo_bp, url_prefix='/todolist')

# default mongodb configuration - Remote database
client = pymongo.MongoClient(
    "mongodb+srv://forix:uwugaming@cluster0.kssld4i.mongodb.net/?retryWrites=true&w=majority")
# database:
db = client.flask_db
# collections:
todos = db.todos
records = db.register


@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    if "email" not in session:
        return redirect(url_for("login"))
    return render_template('index.html')


# This method will handle the registration of a client
@app.route("/register/", methods=['post', 'get'])
def register():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('register.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('register.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('register.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)

            user_data = records.find_one({"email": email})
            new_email = user_data['email']

            return render_template('logged_in.html', email=new_email)
    return render_template('register.html')


@app.route('/about/')
def about():
    message = ''
    if "email" not in session:
        return redirect(url_for("login"))

    return render_template('about.html')


# This method will handle the login of a client
@app.route("/login/", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


# This method is a checker to see if a client is logged-in or not.
@app.route('/logged_in/')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))


# This method will handle the logout of an logged-in account
@app.route("/logout/", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("sign_out.html")
    else:
        return render_template('index.html')


@app.route('/todolist/', methods=('GET', 'POST'))
# The view  that will display the todo list
def todolist():
    message = ''
    if "email" not in session:
        return redirect(url_for("login"))

    # Inside this if section, form submission will be processed
    if request.method == 'POST':
        # This part will handle the todo creation to the database
        if 'create' in request.form:
            content = request.form['content']
            degree = request.form['degree']
            todos.insert_one({'content': content, 'degree': degree})
            test = todos.find_one({'content': content})
        # This part will handle the filter display
        if 'ok' in request.form:
            checked = request.form['filter']
            if checked != 'anything':
                all_todos = todos.find()
                test = []
                for actual in all_todos:
                    if actual['degree'] == checked:
                        test.append(actual)
                return render_template('todolist.html', todos=test, selected=checked)
        return redirect(url_for('todolist'))

    all_todos = todos.find()
    return render_template('todolist.html', todos=all_todos, selected='anything')


# This method is used to edit the informations of a TODO
@app.route('/<id>/edit', methods=('GET', 'POST'))
def edit(id):
    message = ''
    if "email" not in session:
        # Will redirect if client is not logged-in
        return redirect(url_for("login"))
    if request.method == 'POST':
        # Retrieve new information to update a todo entry
        content = request.form['content']
        degree = request.form['degree']
        todos.replace_one({"_id": ObjectId(id)}, {'content': content, 'degree': degree})
        return redirect(url_for('todolist'))
    # Search for a todo with an given id in the link
    todo = todos.find_one({"_id": ObjectId(id)})
    return render_template('edit.html', important=(todo['degree'] == 'Important'), todo=todo['content'])


@app.post('/<id>/delete')
# This view will delete a todo from the database and it will instantly redirect to todo todoList view
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('todolist'))


if __name__ == '__main__':
    app.run()
