import sqlite3

def init_db():
    conn = sqlite3.connect('webserver.db') # user 정보와 게시판 관리 DB 통합
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            profile     TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            content     TEXT NOT NULL,
            author      INTEGER NOT NULL,
            FOREIGN KEY (author) REFERENCES accounts(id)
        )
    ''')
    # id: 기본 키, FOREIGN: 외래 키
    # 게시판 관련 테이블 추가
    # 외래 키란? 이 테이블이 다른 테이블과 관계가 있다는 것을 나타냄.
    conn.commit()
    conn.close()


def add_account(username, password):
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
    '''
    INSERT INTO accounts
    (username, password, profile)
    VALUES (?, ?, ?)
    ''',
    (
        username,
        password,
        f'{username}의 프로필 정보'
    )
)
        conn.commit()
        conn.close()
        return True # success
    except sqlite3.IntegrityError:
        conn.close()
        return False # failure
    

def check_account(username, password):
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()

    query = f"""  
        SELECT * FROM accounts
        WHERE username = '{username}'
        AND password = '{password}'
    """
    # SQLi 취약 코드. 사용자 입력이 SQL 구문으로 직접 삽입 되어서 사용자 입력값이 SQL 문장의 일부로 해석됨.
    print('[DEBUG SQL]', query)

    cursor.execute(query)

    user = cursor.fetchone()

    conn.close()

    return user

# def check_account(username, password):
#     conn = sqlite3.connect('webserver.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM accounts WHERE username = ? AND password = ?',
#                    (username, password))
#     user = cursor.fetchone()
#     conn.close()
#     return user
# 안전한 코드 예시. Parameterized Query를 사용해 입력값을 SQL 문법으로 


def get_all_posts(): # 게시글 목록 반환
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT posts.id, posts.title, accounts.username
        FROM posts JOIN accounts
        ON posts.author = accounts.id
    ''')
    # id, title, username을 가져옴
    # posts와 accounts에서
    # posts.author 값과 accounts.id 값이 같은 데이터끼리 연결함
    posts = cursor.fetchall()
    conn.close()
    return posts

def get_user_by_id(user_id):
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT id, username, profile
        FROM accounts
        WHERE id = ?
        ''',
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


def create_post(title, content, author_id):
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO posts (title, content, author) VALUES (?, ?, ?)',
                   (title, content, author_id))
    # 게시글 제목(title), 내용(content), 작성자 고유번호(author_id)를 posts에 추가
    # posts 테이블에
    # title, content, author 열에 title, content, author_id를 추가
    conn.commit()
    conn.close()


def get_post_by_post_id(post_id): # post_id 추가
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT posts.id, posts.title, posts.content, accounts.username
        FROM posts JOIN accounts
        ON posts.author = accounts.id
        WHERE posts.id = ?
    ''', (post_id,)) # 파이썬 sqlite3에서 단일 인자는 튜플 형태 (값,)로 전달해야 안전합니다.
    # posts.id, posts.title, posts.content, accounts.username을 가져와라
    # posts와 accounts 테이블에서
    # posts.author 값과 accounts.id 값이 같은 데이터끼리 연결함
    # id가 인자로 전달 받은 post_id인 게시글만 가져오도록 조건
    post = cursor.fetchone()
    # 호출 시 게시글 고유 번호, 게시글 내용 등이 튜플 형태로 반환됨.
    conn.close()
    return post


def update_post(post_id, new_title, new_content):
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?',
                   (new_title, new_content, post_id))
    # posts 테이블의 데이터 수정
    # new_title, new_content로
    # id가 posts_id와 일치하는 게시글 데이터만 수정하겠다는 의미
    conn.commit()
    conn.close()


def delete_post(post_id): # 게시글 삭제 기능
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,)) # 단일 인자 튜플화 (, 추가)
    # posts 테이블로 부터
    # id가 post_id인 게시글 삭제
    conn.commit()
    conn.close()