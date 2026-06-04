from flask import Flask, redirect, render_template, request, session, url_for
import os
from db import init_db, check_account, add_account, get_all_posts, create_post, get_post_by_post_id, update_post, delete_post, get_user_by_id

app = Flask(__name__)
app.secret_key = os.urandom(32)


@app.route('/', methods=['GET'])
def get_index():
    if 'username' not in session:
        return redirect(url_for('get_login'))

    return render_template('index.html', username=session['username'],user_id=session['user_id'])


@app.route('/posts', methods=['GET']) # 게시판 목록 조회
def get_posts():
    if 'username' not in session: 
        return redirect(url_for('get_login')) # 로그인 되어 있지 않으면 login 창으로 돌아가고

    posts = get_all_posts() # 아니면 get_all_posts에서 posts 변수에 대입
    return render_template('posts.html', posts=posts) # posts라는 이름으로 posts.html 반환


@app.route('/posts/new', methods=['GET']) # 게시글 생성
def get_posts_new():
    if 'username' not in session:
        return redirect(url_for('get_login'))

    return render_template('posts_new.html') # 로그인 되어 있지 않으면 get_login 호출


@app.route('/posts/new', methods=['POST']) # 게시글 생성
def post_posts_new():
    if 'username' not in session: 
        return redirect(url_for('get_login')) # 로그인 되어 있지 않으면 get_login 호출

    title = request.form.get('title')
    content = request.form.get('content')
    author_id = session['user_id']
    create_post(title, content, author_id)
    # 제목과 내용으로 글 생성
    return redirect(url_for('get_posts')) # get_posts 호출


@app.route('/posts/<post_id>', methods=['GET']) # 게시글 보여주기
# post_id 위치에 오는 모든 값을 경로 매개변수로 사용(<>를 의미)
def get_posts_post_id(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)
    if post:
        return render_template('post.html', post=post)
    else:
        return redirect(url_for('get_posts'))
    # 게시글의 고유 번호를 전달하면 게시글의 내용을 이용자에게 보여줌.


@app.route('/posts/<post_id>/edit', methods=['GET']) # 게시글 수정 
# post_id에서 오는 값 경로 매개변수
def get_posts_post_id_edit(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login')) # 로그인 상태 아니면 로그인 페이지로

    post = get_post_by_post_id(post_id)
    if not post:
        return redirect(url_for('get_posts'))
        # post가 유효하지 않으면 get_posts 호출

    if post[3] != session['username']: # 게시글 작성자의 유저네임이 현재 로그인된 이용자의 유저네임과 동일한지 검사
        return render_template('post_edit_failure.html') # 동일하지 않다면 수정 실패, post_edit_failure.html 반환

    return render_template('post_edit.html', post=post)


@app.route('/posts/<post_id>/edit', methods=['POST']) # 게시글 수정 
# post_id에서 오는 값 경로 매개변수
def post_posts_post_id_edit(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login')) # 로그인 상태 아니면 로그인 페이지로

    post = get_post_by_post_id(post_id)
    if not post: 
        return redirect(url_for('get_posts'))
        # post가 유효하지 않으면 get_posts 호출

    if post[3] != session['username']: # 게시글 작성자의 유저네임이 현재 로그인된 이용자의 유저네임과 동일한지 검사
        return render_template('post_edit_failure.html') # 동일하지 않다면 수정 실패, post_edit_failure.html 반환

    title = request.form.get('title')
    content = request.form.get('content')
    update_post(post_id, title, content)
    # title과 content와 update_post로 게시글 수정
    return redirect(url_for('get_posts_post_id', post_id=post_id))


@app.route('/posts/<post_id>/delete', methods=['GET']) # 게시글 삭제
def get_posts_post_id_delete(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id) # post_id로 조회
    if not post:
        return redirect(url_for('get_posts'))

    if post[3] != session['username']: # 작성자가 username에 없으면 post_delete_failure 반환
        return render_template('post_delete_failure.html')

    return render_template('post_delete.html', post=post)
    # 이용자가 게시글 작성자이면 delete 페이지 반환


@app.route('/posts/<post_id>/delete', methods=['POST'])
def post_posts_post_id_delete(post_id):
    if 'username' not in session:
        return redirect(url_for('get_login'))

    post = get_post_by_post_id(post_id)
    if not post:
        return redirect(url_for('get_posts'))

    if post[3] != session['username']:
        return render_template('post_delete_failure.html')
      # 작성자가 username에 없으면 post_delete_failure 반환
        # 이용자가 게시글 작성자이면 delete 페이지 반환

    delete_post(post_id) # 삭제
    return redirect(url_for('get_posts')) # 게시글 목록 페이지로 호출


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
    else:
        return render_template('register_failure.html')


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
    user = check_account(username, password) # check_account 검증
    if user:
        session['user_id'] = user[0] # session의 user_id에 user[0] 대입
        session['username'] = user[1] # session의 username에 user[1] 대입
        return redirect(url_for('get_index'))
    else:
        return render_template('login_failure.html')
        # check_account는 user_id 와 username을 튜플로 변환. user[0]는 이용자 고유 번호, user[1]은 유저 네임이 됨.


@app.route('/logout', methods=['GET'])
def get_logout():
    session.clear()
    return redirect(url_for('get_login'))

@app.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):

    if 'username' not in session:
        return redirect(url_for('get_login'))

    user = get_user_by_id(user_id)

    if not user:
        return redirect(url_for('get_index'))

    return render_template(
        'profile.html',
        user=user
    )

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=31337)