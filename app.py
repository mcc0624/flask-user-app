from flask import Flask, render_template, request, redirect, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "dev-key-2025"

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

    conn = sqlite3.connect(db_path)
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

    # 插入默认用户，使用 INSERT OR IGNORE 防止重复插入
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES ('admin', 'admin123', 'admin@example.com', '13800138000')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, phone) VALUES ('alice', 'alice2025', 'alice@example.com', '13900139001')")

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
        conn = sqlite3.connect(db_path)
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
        conn = sqlite3.connect(db_path)
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


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8081, debug=True)
