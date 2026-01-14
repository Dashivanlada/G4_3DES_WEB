from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from crypto_3des import encrypt, decrypt

web = Flask(__name__)
web.secret_key = "secret-key-3des"

def get_db():
    return sqlite3.connect("data.db")

def login_required():
    return 'user_id' in session

@web.route('/')
def home():
    return redirect('/login')

# REGISTER
@web.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = generate_password_hash(request.form['password'])

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?,?)",
                (user, pwd)
            )
            db.commit()
        except:
            pass
        db.close()
        return redirect('/login')

    return render_template("register.html")

# LOGIN
@web.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        db = get_db()
        cur = db.execute(
            "SELECT id, password_hash FROM users WHERE username=?",
            (user,)
        )
        row = cur.fetchone()
        db.close()

        if row and check_password_hash(row[1], pwd):
            session['user_id'] = row[0]
            return redirect('/notes')

    return render_template("login.html")

@web.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# LIST NOTES
@web.route('/notes')
def notes():
    if not login_required():
        return redirect('/login')

    uid = session['user_id']
    db = get_db()
    cur = db.execute("SELECT id FROM notes WHERE owner_id=?", (uid,))
    notes = cur.fetchall()
    db.close()

    return render_template("notes.html", notes=notes)

# CREATE NOTE
@web.route('/create', methods=['GET','POST'])
def create():
    if not login_required():
        return redirect('/login')

    if request.method == 'POST':
        msg = request.form['message']
        pwd = request.form['password']
        cipher = encrypt(msg, pwd)

        db = get_db()
        db.execute(
            "INSERT INTO notes (content, owner_id) VALUES (?,?)",
            (cipher, session['user_id'])
        )
        db.commit()
        db.close()
        return redirect('/notes')

    return render_template("create.html")

# VIEW NOTE
@web.route('/note/<int:id>', methods=['GET','POST'])
def note(id):
    if not login_required():
        return redirect('/login')

    db = get_db()
    cur = db.execute(
        "SELECT content FROM notes WHERE id=? AND owner_id=?",
        (id, session['user_id'])
    )
    row = cur.fetchone()
    db.close()

    if not row:
        return "Not found"

    text = None
    error = None

    if request.method == 'POST':
        try:
            text = decrypt(row[0], request.form['password'])
        except:
            error = "❌ Incorrect password"

    return render_template("note.html", text=text, error=error)

if __name__ == "__main__":
    web.run(host="0.0.0.0", port=5000)

