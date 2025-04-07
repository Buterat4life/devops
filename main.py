from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)

POSTS_FILE = 'data/posts.json'
LOG_FILE = 'logs/access.log'

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

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        posts = load_posts()
        new_post = {
            "id": get_next_id(posts),
            "title": request.form['title'],
            "content": request.form['content'],
            "owner_id": get_next_id(posts)
        }
        posts.append(new_post)
        save_posts(posts)
        return redirect('/')
    return render_template('create.html')

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    posts = load_posts()
    updated_posts = [post for post in posts if post['id'] != post_id]
    save_posts(updated_posts)
    return redirect('/')

if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    app.run(debug=True)

