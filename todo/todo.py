'''from flask import Blueprint, Flask, render_template, request, url_for, redirect, session
import pymongo
from bson import ObjectId

# default mongodb configuration - Remote database
client = pymongo.MongoClient(
    "mongodb+srv://cafe:yYCEj4BSsl0zgifW@cluster0.lz9tjnm.mongodb.net/?retryWrites=true&w=majority")
# database:
db = client.flask_db
# collections:
todos = db.todos
records = db.register

todo_bp = Blueprint('todo_bp', __name__, template_folder='templates', static_folder='static')


@app.route('/todolist', methods=('GET', 'POST'))
def todolist():
    message = ''
    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == 'POST':
        content = request.form['content']
        degree = request.form['degree']
        todos.insert_one({'content': content, 'degree': degree})
        return redirect(url_for('todolist'))

    all_todos = todos.find()
    return render_template('/todolist', todos=all_todos)


@app.post('/<id>/delete')
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))
    '''

