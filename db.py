import sqlite3


# =========================
# Database 시작
# =========================

def init_db():
    conn = sqlite3.connect('webserver.db')
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

    # accounts : 사용자 정보
    # posts    : 게시판 정보

    conn.commit()
    conn.close()


# =========================
# Account
# =========================

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
                f'{username}의 프로필'
            )
        )

        conn.commit()
        conn.close()

        return True

    except sqlite3.IntegrityError:
        conn.close()

        return False


def check_account(username, password):
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()

    query = f'''
        SELECT *
        FROM accounts
        WHERE username = '{username}'
        AND password = '{password}'
    '''

    # SQL Injection 실습용 취약 코드
    # 사용자 입력이 SQL 구문에 직접 삽입됨
    print('[DEBUG SQL]', query)

    cursor.execute(query)

    user = cursor.fetchone()

    conn.close()

    return user


# =========================
# Safe Example
# =========================

# def check_account(username, password):
#     conn = sqlite3.connect('webserver.db')
#     cursor = conn.cursor()
#
#     cursor.execute(
#         '''
#         SELECT *
#         FROM accounts
#         WHERE username = ?
#         AND password = ?
#         ''',
#         (username, password)
#     )
#
#     user = cursor.fetchone()
#
#     conn.close()
#
#     return user

# Parameterized Query 사용
# 사용자 입력이 SQL 문법이 아닌 데이터로 처리됨


# =========================
# Profile
# =========================

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


# =========================
# Posts
# =========================

def get_all_posts():
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT
            posts.id,
            posts.title,
            accounts.username
        FROM posts
        JOIN accounts
            ON posts.author = accounts.id
        '''
    )

    posts = cursor.fetchall()

    conn.close()

    return posts


def create_post(title, content, author_id):
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO posts
        (title, content, author)
        VALUES (?, ?, ?)
        ''',
        (title, content, author_id)
    )

    conn.commit()
    conn.close()


def get_post_by_post_id(post_id):
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT
            posts.id,
            posts.title,
            posts.content,
            accounts.username
        FROM posts
        JOIN accounts
            ON posts.author = accounts.id
        WHERE posts.id = ?
        ''',
        (post_id,)
    )

    post = cursor.fetchone()

    conn.close()

    return post


def update_post(post_id, new_title, new_content):
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        UPDATE posts
        SET
            title = ?,
            content = ?
        WHERE id = ?
        ''',
        (
            new_title,
            new_content,
            post_id
        )
    )

    conn.commit()
    conn.close()


def delete_post(post_id):
    conn = sqlite3.connect('webserver.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        DELETE FROM posts
        WHERE id = ?
        ''',
        (post_id,)
    )

    conn.commit()
    conn.close()