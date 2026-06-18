from flask import Flask, redirect, render_template, request, session, url_for
import os

from db import (
    init_db,
    check_account,
    add_account,
    get_all_posts,
    create_post,
    get_post_by_post_id,
    update_post,
    delete_post,
    get_user_by_id
)

app = Flask(__name__)
app.secret_key = os.urandom(32) # 난수 생성


# =========================
# Main
# =========================

@app.route('/', methods=['GET'])
def get_index():
    # 로그인 여부 확인
    if 'username' not in session:
        return redirect(url_for('get_login'))

    return render_template(
        'index.html',
        username=session['username'],
        user_id=session['user_id']
    )


# =========================
# Posts
# =========================

@app.route('/posts', methods=['GET'])
def get_posts():
    # 로그인 여부 확인
    if 'username' not in session:
        return redirect(url_for('get_login'))

    posts = get_all_posts()

    return render_template(
        'posts.html',
        posts=posts
    )


@app.route('/posts/new', methods=['GET'])
def get_posts_new():
    # 로그인 여부 확인
    if 'username' not in session:
        return redirect(url_for('get_login'))

    return render_template('posts_new.html')


@app.route('/posts/new', methods=['POST'])
def post_posts_new():
    # 로그인 여부 확인
    if 'username' not in session:
        return redirect(url_for('get_login'))

    title = request.form.get('title')
    content = request.form.get('content')
    author_id = session['user_id']

    create_post(title, content, author_id)

    return redirect(url_for('get_posts'))


@app.route('/posts/<post_id>', methods=['GET'])
def get_posts_post_id(post_id):
    # 로그인 여부 확인
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)

    if post:
        return render_template('post.html', post=post)

    return redirect(url_for('get_posts'))


@app.route('/posts/<post_id>/edit', methods=['GET'])
def get_posts_post_id_edit(post_id):
    # 로그인 여부 확인
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)

    if not post:
        return redirect(url_for('get_posts'))

    # 게시글 작성자가 현재 로그인 사용자와 같은지 확인
    if post[3] != session['username']:
        return render_template('post_edit_failure.html')

    return render_template(
        'post_edit.html',
        post=post
    )


@app.route('/posts/<post_id>/edit', methods=['POST'])
def post_posts_post_id_edit(post_id):
    # 로그인 여부 확인
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)

    if not post:
        return redirect(url_for('get_posts'))

    # 게시글 작성자가 현재 로그인 사용자와 같은지 확인
    if post[3] != session['username']:
        return render_template('post_edit_failure.html')

    title = request.form.get('title')
    content = request.form.get('content')

    update_post(post_id, title, content)

    return redirect(
        url_for(
            'get_posts_post_id',
            post_id=post_id
        )
    )


@app.route('/posts/<post_id>/delete', methods=['GET'])
def get_posts_post_id_delete(post_id):
    # 로그인 여부 확인
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)

    if not post:
        return redirect(url_for('get_posts'))

    # 게시글 작성자가 현재 로그인 사용자와 같은지 확인
    if post[3] != session['username']:
        return render_template('post_delete_failure.html')

    return render_template(
        'post_delete.html',
        post=post
    )


@app.route('/posts/<post_id>/delete', methods=['POST'])
def post_posts_post_id_delete(post_id):
    # 로그인 여부 확인
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)

    if not post:
        return redirect(url_for('get_posts'))

    # 게시글 작성자가 현재 로그인 사용자와 같은지 확인
    if post[3] != session['username']:
        return render_template('post_delete_failure.html')

    delete_post(post_id)

    return redirect(url_for('get_posts'))


# =========================
# Register
# =========================

@app.route('/register', methods=['GET'])
def get_register():
    if 'username' in session:
        return redirect(url_for('get_index'))

    return render_template('register.html')


@app.route('/register', methods=['POST'])
def post_register():
    if 'username' in session:
        return redirect(url_for('get_index'))

    username = request.form.get('username')
    password = request.form.get('password')

    if add_account(username, password):
        return redirect(url_for('get_login'))

    return render_template('register_failure.html')


# =========================
# Login / Logout
# =========================

@app.route('/login', methods=['GET'])
def get_login():
    if 'username' in session:
        return redirect(url_for('get_index'))

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def post_login():
    if 'username' in session:
        return redirect(url_for('get_index'))

    username = request.form.get('username')
    password = request.form.get('password')

    user = check_account(username, password)

    if user:
        # 로그인 성공 시 세션 저장
        session['user_id'] = user[0]
        session['username'] = user[1]

        return redirect(url_for('get_index'))

    return render_template('login_failure.html')


@app.route('/logout', methods=['GET'])
def get_logout():
    session.clear()

    return redirect(url_for('get_login'))


# =========================
# Profile
# =========================

@app.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    # 로그인 여부 확인
    if 'username' not in session:
        return redirect(url_for('get_login'))

    # IDOR 실습용 프로필 조회
    user = get_user_by_id(user_id)

    if not user:
        return redirect(url_for('get_index'))

    return render_template(
        'profile.html',
        user=user
    )


# =========================
# 실행
# =========================

if __name__ == '__main__':
    # 웹 서버 실행
    init_db()
    app.run(host='0.0.0.0', port=31337)