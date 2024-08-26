from flask import Flask, render_template, request,g, jsonify, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True
app.config['DATABASE'] = 'users.db'
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_table():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                password TEXT
            )
        ''')
        db.commit()

def initialize_database():
    if not os.path.exists(app.config['DATABASE']):
        create_table()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        authenticated = authenticate_user(email, password)
        if authenticated:
            session['logged_in'] = True
            session['email'] = email
            return redirect(url_for('user_list'))
        else:
            return 'invalid credentials. <br> Back to <a href=/>Login</a>'
  
def authenticate_user(email, password):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        if user:
            return True
    return False

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/users')
def user_list():
    users = []
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        for row in rows:
            user = {
                'id': row[0],
                'email': row[1],
                'password': row[2]
            }
            users.append(user)
    return render_template('users.html', users=users)

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        db.commit()
        return 'User signed up successfully! <br>You can now <a href=/>Log in</a>'
    except sqlite3.IntegrityError:
        return 'User with that email already exists.'
    
@app.route('/usersapi')
def usersapi():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    user_list = []
    for user in users:
        user_dict = {
            'id': user[0],
            'email': user[1],
            'password': user[2]
        }
        user_list.append(user_dict)
    return jsonify(user_list)

@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        if(len(cursor.fetchall())>0):
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            db.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': "No user with that id"})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    with app.app_context():
        initialize_database()
    app.run(host='0.0.0.0')