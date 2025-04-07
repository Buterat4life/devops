from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(name)

POSTS_FILE = 'data/posts.json'
LOG_FILE = 'logs/access.log'

# Загрузка постов
def load_posts():
    with open(POSTS_FILE, 'r') as f:
        return json.load(f)

# Логирование обращений
def log_access(ip, user_id, accessed_post):
    with open(LOG_FILE, 'a') as f:
        f.write(f'{datetime.now()} - IP: {ip}, User ID: {user_id}, Accessed Post ID: {accessed_post}\n')

@app.route('/')
def index():
    posts = load_posts()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    user_id = request.args.get('user', 'anonymous')
    ip = request.remote_addr
    log_access(ip, user_id, post_id)

    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            return render_template('post.html', post=post, user_id=user_id)
    return "Пост не найден", 404

if name == 'main':
    os.makedirs('logs', exist_ok=True)
    app.run(debug=True)