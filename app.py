from flask import Flask, render_template, request, redirect, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "dev-key-2025"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 用户数据库 - 明文密码存储（保持原有登录功能不变）
USERS = {
    "admin": {
        "username": "admin",
        "password": "admin123",
        "role": "admin",
        "email": "admin@example.com",
        "phone": "13800138000",
        "balance": 99999
    },
    "alice": {
        "username": "alice",
        "password": "alice2025",
        "role": "user",
        "email": "alice@example.com",
        "phone": "13900139001",
        "balance": 100
    }
}


def init_db():
    """初始化 SQLite 数据库"""
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "users.db")

    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()

    # 创建 users 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            phone TEXT
        )
    """)

    # 添加 balance 字段（兼容已有数据库）
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # 插入默认用户，使用 INSERT OR IGNORE 防止重复插入
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES ('admin', 'admin123', 'admin@example.com', '13800138000')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES ('alice', 'alice2025', 'alice@example.com', '13900139001')")

    # 设置默认用户余额
    cursor.execute("UPDATE users SET balance = 99999 WHERE username = 'admin'")
    cursor.execute("UPDATE users SET balance = 100 WHERE username = 'alice'")

    conn.commit()
    conn.close()


@app.route("/")
def index():
    username = session.get("username")
    user_info = None
    if username and username in USERS:
        user_info = USERS[username]
    return render_template("index.html", user=user_info)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username in USERS and USERS[username]["password"] == password:
            session["username"] = username
            user_info = USERS[username]
            return render_template("index.html", user=user_info)
        else:
            return render_template("login.html", error="用户名或密码错误！")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        email = request.form.get("email", "")
        phone = request.form.get("phone", "")

        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "users.db")
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()

        # 使用 f-string 字符串拼接方式插入数据
        sql = f"INSERT INTO users (username, password, email, phone) VALUES ('{username}', '{password}', '{email}', '{phone}')"
        print(f"[REGISTER SQL] {sql}")
        cursor.execute(sql)
        conn.commit()
        conn.close()

        return render_template("login.html", success="注册成功，请登录")

    return render_template("register.html")


@app.route("/search")
def search():
    keyword = request.args.get("keyword", "")
    username = session.get("username")
    user_info = None
    if username and username in USERS:
        user_info = USERS[username]

    results = []
    if keyword:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "users.db")
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()

        # 使用 f-string 字符串拼接方式拼接 SQL 查询
        sql = f"SELECT * FROM users WHERE username LIKE '%{keyword}%' OR email LIKE '%{keyword}%'"
        print(f"[SEARCH SQL] {sql}")
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            results.append({
                "id": row[0],
                "username": row[1],
                "password": row[2],
                "email": row[3],
                "phone": row[4]
            })

    return render_template("index.html", user=user_info, keyword=keyword, results=results)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    # 需要登录才能访问
    if not session.get("username"):
        return redirect("/login")

    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return render_template("upload.html", error="请选择要上传的文件")

        # 创建 uploads 目录
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # 使用用户上传的原始文件名保存
        file.save(os.path.join(upload_dir, file.filename))

        file_url = f"/static/uploads/{file.filename}"
        return render_template("upload.html", success=True, filename=file.filename, file_url=file_url)

    return render_template("upload.html")


@app.route("/profile")
def profile():
    user_id = request.args.get("user_id", "")

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "users.db")
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()

    sql = f"SELECT * FROM users WHERE id = {user_id}"
    print(f"[PROFILE SQL] {sql}")
    cursor.execute(sql)
    row = cursor.fetchone()
    conn.close()

    user_data = None
    if row:
        user_data = {
            "id": row[0],
            "username": row[1],
            "email": row[3],
            "phone": row[4],
            "balance": row[5] if len(row) > 5 else 0
        }

    return render_template("profile.html", user=user_data)


@app.route("/recharge", methods=["POST"])
def recharge():
    user_id = request.form.get("user_id", "")
    amount = request.form.get("amount", "0")

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "users.db")
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()

    sql = f"UPDATE users SET balance = balance + {amount} WHERE id = {user_id}"
    print(f"[RECHARGE SQL] {sql}")
    cursor.execute(sql)
    conn.commit()
    conn.close()

    return redirect(f"/profile?user_id={user_id}")


@app.route("/page")
def page():
    name = request.args.get("name", "")
    page_content = None

    # 构建文件路径 - 直接拼接用户输入，不做任何校验
    page_path = os.path.join("pages", name)
    if os.path.exists(page_path):
        with open(page_path, "r", encoding="utf-8") as f:
            page_content = f.read()
    else:
        # 尝试加 .html 后缀
        page_path_html = page_path + ".html"
        if os.path.exists(page_path_html):
            with open(page_path_html, "r", encoding="utf-8") as f:
                page_content = f.read()

    if page_content is None:
        page_content = "页面不存在"

    # 获取用户信息
    username = session.get("username")
    user_info = None
    if username and username in USERS:
        user_info = USERS[username]

    return render_template("index.html", user=user_info, page_content=page_content)


@app.route("/change-password", methods=["POST"])
def change_password():
    username = request.form.get("username", "")
    new_password = request.form.get("new_password", "")

    # 更新内存中的 USERS 字典
    if username in USERS:
        USERS[username]["password"] = new_password

    # 同时更新 SQLite 数据库
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "users.db")
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()
    sql = f"UPDATE users SET password = '{new_password}' WHERE username = '{username}'"
    print(f"[CHANGE_PASSWORD SQL] {sql}")
    cursor.execute(sql)
    conn.commit()
    conn.close()

    return redirect("/profile")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8081, debug=True, use_reloader=False)
