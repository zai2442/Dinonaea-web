# Dionaea-web系统启动说明

整个系统包括**分析平台**和**蜜罐**两部分，具体启动方法如下：

## 1. 蜜罐模块 (web_dionaea) 启动

蜜罐模块位于 `Dionaea/web_dionaea` 目录下，基于 Python 2 + Django 1.9.8 开发。

### 方式一：Docker 部署（推荐）
```bash
cd Dionaea/web_dionaea
# 1. 制作蜜罐镜像
docker build -t "web_dionaea" .
# 2. 创建并运行容器
docker run -d -p 80:80 -v /opt:/tmp --restart=always web_dionaea
# 3. 添加计划任务 (CentOS7 环境演示)
# */5 * * * * /bin/bash /opt/Check.sh 
```

### 方式二：本地部署
```bash
cd Dionaea/web_dionaea
# 建立并激活虚拟环境 (需提前安装好python2及virtualenv)
virtualenv -p python2 venv
source venv/bin/activate
# 安装依赖
pip install django==1.9.8 
# 执行数据库迁移
python manage.py migrate
# 启动服务
python manage.py runserver 0.0.0.0:8000
```

---

## 2. 分析平台启动

分析平台包含 FastAPI 构建的后端系统和 HTML/JS 构建的前端页面。

### 2.1 前置服务部署 (数据库与 Redis)
分析平台依赖 **PostgreSQL 15+** 和 **Redis 7+**。
我们推荐使用项目下提供的 `docker-compose.yml` 来一键部署这两个数据库服务。

1. 进入工作目录：
```bash
cd Dionaea
```

2. (可选) 查看 `docker-compose.yml` 配置，默认的数据库账号和密码如下：
- PostgreSQL: `POSTGRES_USER=user`, `POSTGRES_PASSWORD=pass`, `POSTGRES_DB=db_name`
- 映射端口分别为 PostgreSQL `5432` 和 Redis `6379`。

3. 启动并后台运行数据库容器：
```bash
docker-compose up -d
```
> 你可以通过 `docker ps` 命令检查 `dionaea_postgres` 和 `dionaea_redis` 容器是否成功处于 Up 状态。

### 2.2 后端启动 (Backend)
要求：Python 3.11+, PostgreSQL 15+, Redis 7+
```bash
cd Dionaea/backend
# 建立并激活虚拟环境
python3 -m venv .venv

source .venv/bin/activate
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境
# 在后端目录下创建 .env 文件，配置 DATABASE_URL, REDIS_URL, SECRET_KEY 等参数
# 参考内容：
# DATABASE_URL=postgresql://user:pass@localhost:5432/db_name
# REDIS_URL=redis://localhost:6379/0
# SECRET_KEY=your_secret_key

# 3. 运行服务
python main.py
# 或使用 uvicorn
# uvicorn app.main:app --reload
```
> 后端启动后，API 文档访问地址为：`http://localhost:8001/docs`

### 2.3 日志采集服务 (Ingestor)
负责实时监控蜜罐生成的日志并同步到分析平台数据库。
```bash
cd Dionaea/backend
source .venv/bin/activate

# 启动日志采集
python ingestor.py
```
> 注意：确保 `ingestor.py` 中的 `MONITOR_DIR` 指向蜜罐日志文件 `Dionaea.log` 所在的目录（默认为 `/tmp`）。

### 2.4 前端启动 (Frontend)
前端为静态构建的 Web 页面。
```bash
cd Dionaea/frontend_login_demo

# 使用 python 启动一个简单的 Web 服务器
python3 -m http.server 8000
```
> 启动后，在浏览器访问：`http://localhost:8000/index.html` 或者 `http://localhost:8000/dashboard.html`
> （可以通过修改 `assets/js/app.js` 中的 `CONFIG` 更换为连接真实后端的 API 模式）