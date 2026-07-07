# 用户信息管理平台

一个基于 **Python Flask** 构建的简易用户信息管理平台，提供基本的用户登录/登出功能，登录后可查看用户完整信息。

> ⚠️ **注意：** 本项目为**教学演示用途**，密码以明文形式存储和传输，请勿用于生产环境。

---

## 功能特性

- ✅ 用户登录 / 登出（基于 Session）
- ✅ 登录后展示用户完整信息（用户名、密码、邮箱、手机、角色、余额）
- ✅ 登录错误提示
- ✅ 响应式卡片式 UI 设计
- ✅ 蓝色渐变导航栏 + 白色卡片布局

---

## 技术栈

| 技术 | 说明 |
|------|------|
| **Python 3** | 编程语言 |
| **Flask** | Web 框架 |
| **Jinja2** | 模板引擎 |
| **CSS3** | 页面样式（Flexbox 布局） |

---

## 项目结构

```
flask-user-app/
├── app.py                  # 主应用文件，Flask 路由与核心逻辑
├── templates/
│   ├── base.html           # 基础模板（导航栏 + 容器）
│   ├── index.html          # 首页（登录后展示用户信息）
│   └── login.html          # 登录页面
├── static/
│   └── css/
│       └── style.css       # 样式文件
└── .gitignore
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/mcc0624/flask-user-app.git
cd flask-user-app
```

### 2. 安装依赖

```bash
pip install flask
```

> 如果遇到系统权限限制，可尝试：
> ```bash
> pip install flask --break-system-packages
> ```

### 3. 启动应用

```bash
python app.py
```

启动后访问 **http://localhost:8081** 即可使用。

---

## 默认测试账号

| 用户名 | 密码 | 角色 | 邮箱 | 手机 | 余额 |
|--------|------|------|------|------|------|
| `admin` | `admin123` | admin | admin@example.com | 13800138000 | 99999 |
| `alice` | `alice2025` | user | alice@example.com | 13900139001 | 100 |

> 💡 登录页 HTML 注释中已包含默认管理员账号信息，方便调试。

---

## 路由说明

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页。已登录显示用户信息，未登录提示登录 |
| `/login` | GET / POST | 登录页。POST 提交用户名和密码进行验证 |
| `/logout` | GET | 登出，清除 Session 后重定向到首页 |

---

## 核心代码示例

### 用户数据库（明文密码）

```python
USERS = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # 明文存储 ⚠️
        "role": "admin",
        "email": "admin@example.com",
        "phone": "13800138000",
        "balance": 99999
    },
    "alice": {
        "username": "alice",
        "password": "alice2025",  # 明文存储 ⚠️
        "role": "user",
        "email": "alice@example.com",
        "phone": "13900139001",
        "balance": 100
    }
}
```

### 登录验证（直接字符串比对）

```python
if username in USERS and USERS[username]["password"] == password:
    session["username"] = username
    # 登录成功后将完整用户信息（含密码）传递给模板
```

---

## 界面预览

### 未登录状态
- 导航栏右侧显示"登录"链接
- 首页展示提示卡片："请先登录" + "前往登录"按钮

### 登录页面
- 卡片式居中布局
- 用户名和密码输入框
- 登录失败时显示红色错误提示

### 已登录状态
- 导航栏显示"欢迎，用户名"和"退出"链接
- 首页以表格形式展示用户完整信息（含密码）

---

## 安全说明

本项目为**教学演示**用途，存在以下安全性问题，**请勿用于生产环境**：

| 问题 | 说明 |
|------|------|
| 🔓 明文密码存储 | 密码直接以字符串形式存储在字典中 |
| 🔓 明文密码传输 | 登录成功后密码随模板渲染返回前端 |
| 🔓 信息泄露 | 登录页 HTML 注释中包含默认管理员账号 |
| 🔓 Secret Key 硬编码 | `secret_key` 直接在代码中写死 |
| 🔓 无 CSRF 保护 | 登录表单未添加 CSRF Token |
| 🔓 无 Rate Limit | 登录接口无频率限制，可暴力破解 |

---

## License

[MIT](LICENSE)
