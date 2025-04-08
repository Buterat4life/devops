from flask import Flask, render_template, request, redirect, session, url_for
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = '37fh47gfjs74jfls'

POSTS_FILE = 'data/posts.json'
LOG_FILE = 'logs/access.log'
USERS_FILE = 'data/users.json'

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username and check_password_hash(user['password'], password):
            return user
    return None

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Загрузка постов
def load_posts():
    with open(POSTS_FILE, 'r') as f:
        return json.load(f)

def save_posts(posts):
    with open(POSTS_FILE, 'w') as f:
        json.dump(posts, f, indent=4)

# Логирование обращений
def log_access(ip, user_id, accessed_post):
    with open(LOG_FILE, 'a') as f:
        f.write(f'{datetime.now()} - IP: {ip}, User ID: {user_id}, Accessed Post ID: {accessed_post}\n')

def get_next_id(posts):
    if not posts:
        return 1
    ids = [post.get("id", 0) for post in posts if isinstance(post.get("id"), int)]
    return max(ids, default=0) + 1

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('posts'))
    return redirect(url_for('login'))

@app.route('/posts')
def posts():
    posts = load_posts()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    ip = request.remote_addr
    user_id = session.get('user_id', 'anonymous')

    log_access(ip, user_id, post_id)

    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            return render_template('post.html', post=post, user_id=user_id)
    return "Пост не найден", 404

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        posts = load_posts()
        new_post = {
            "id": get_next_id(posts),
            "title": request.form['title'],
            "content": request.form['content'],
            "owner_id": session['user_id']
        }
        posts.append(new_post)
        save_posts(posts)
        return redirect('/posts')
    return render_template('create.html')

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    posts = load_posts()
    updated_posts = [post for post in posts if post['id'] != post_id]
    save_posts(updated_posts)
    return redirect('/posts')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticate(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/posts')
        return render_template('login.html', error='Неверный логин или пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        if any(user['username'] == username for user in users):
            return render_template('register.html', error='Пользователь уже существует')

        new_user = {
            "id": max([u['id'] for u in users], default=0) + 1,
            "username": username,
            "password": generate_password_hash(password)
        }

        users.append(new_user)
        save_users(users)
        return redirect('/login')

    return render_template('register.html')

if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)

