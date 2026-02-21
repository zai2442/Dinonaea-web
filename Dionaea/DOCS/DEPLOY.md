# 部署文档 (Deployment Documentation)

## 1. 环境要求
- **操作系统**: Linux (推荐 Ubuntu/Kali/CentOS)
- **依赖软件**:
  - Python 3.10+
  - PostgreSQL (或使用 SQLite 用于开发)
  - Redis (用于缓存)
  - Apache2 (用于压力测试 `ab`，可选)

## 2. 后端部署

### 2.1 数据库配置
确保 `backend/.env` (或 `config.py` 默认值) 指向正确的数据库。默认使用 SQLite 方便测试。
生产环境建议使用 PostgreSQL。

### 2.2 Redis 配置
使用 Docker 启动 Redis：
```bash
docker-compose up -d redis
```

### 2.3 依赖安装
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# 确保安装了 Redis 客户端和 Uvicorn
pip install redis uvicorn
```

### 2.4 启动服务
```bash
# 在 backend 目录下
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8001
```
API 文档访问地址: `http://localhost:8001/docs`

### 2.5 日志采集器
配置 Dionaea 日志路径环境变量，并运行采集脚本：
```bash
export DIONAEA_LOG_PATH=/opt/Dionaea.log
python backend/ingestor.py
```
建议配置 Systemd 服务或 Crontab 定期运行采集器。

## 3. 前端部署

### 3.1 静态文件
前端为纯静态 HTML/JS 项目。将 `frontend_login_demo` 目录部署到任何 Web 服务器 (Nginx/Apache)。

### 3.2 配置 API 地址
修改 `frontend_login_demo/assets/js/dashboard.js`:
```javascript
const CONFIG = {
    API_BASE: 'http://<YOUR_BACKEND_IP>:8001/api/v1',
    LOGIN_URL: 'index.html'
};
```

## 4. 脚本集成
### 4.1 Check.sh
配置 Crontab 每 5 分钟运行一次：
```bash
*/5 * * * * /bin/bash /home/kali/Dionaea/Dinonaea-web/Dionaea/Check.sh
```
该脚本会自动检测日志变化，并触发 `Login_statistics.sh` 和后端缓存刷新。

## 5. 功能说明
- **系统监控**: 展示实时攻击日志 (支持分页、筛选)。
- **数据统计**:
  - TOP 10 攻击源 IP (柱状图)
  - TOP 5 用户名占比 (饼图)
  - TOP 20 密码词云
- **统计摘要**: 显示最频繁的攻击 IP、用户名和密码 (与 `Login_statistics.sh` 联动)。
