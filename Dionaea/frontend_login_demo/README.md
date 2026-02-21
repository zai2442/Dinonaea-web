# Dionaea Login Page Frontend Implementation

这是一个基于原生 HTML5, Tailwind CSS 和 Vanilla JavaScript 实现的现代化登录页面，旨在作为 Dionaea 后台管理系统的前端原型。

## 目录结构

```
frontend_login_demo/
├── index.html              # 主页面文件
├── assets/
│   ├── css/
│   │   └── style.css       # 自定义样式与动画
│   └── js/
│       └── app.js          # 交互逻辑与 API 集成
├── tests/
│   ├── test_login.py       # Playwright 自动化测试脚本
│   └── README.md           # 测试说明
└── README.md               # 项目说明文档
```

## 功能特性

1.  **现代化 UI 设计**:
    *   响应式布局，适配 PC (1920x1080) 和移动端。
    *   使用 Tailwind CSS 框架，结合自定义动画。
    *   平滑的交互体验（按钮加载状态、输入框聚焦特效）。

2.  **完整的功能逻辑**:
    *   表单验证（必填项检查）。
    *   "记住我" 功能（本地存储用户名）。
    *   API 集成（支持真实后端与 Mock 模式切换）。
    *   错误处理与提示（抖动动画、全局错误提示）。

3.  **无障碍支持**:
    *   ARIA 标签。
    *   键盘导航支持。

## 快速开始

### 1. 运行页面

直接在浏览器中打开 `index.html` 文件即可预览效果。

为了避免跨域问题（CORS）或文件协议限制，建议使用简单的 HTTP 服务器运行：

```bash
# 在项目根目录下运行
python3 -m http.server 8000
```

然后访问: `http://localhost:8000/index.html`

### 2. 配置后端 API

默认情况下，项目处于 **Mock 模式** (`MOCK_MODE = true`)，无需后端即可体验完整流程。
输入任意用户名和密码（Mock 逻辑中预设 `admin / password` 为成功凭证）。

若要连接真实后端：
1.  打开 `assets/js/app.js`。
2.  修改配置：
    ```javascript
    const CONFIG = {
        API_URL: '/api/v1/auth/login', // 修改为您的后端地址
        DASHBOARD_URL: '/dashboard.html',
        MOCK_MODE: false // 关闭 Mock 模式
    };
    ```

## 测试

本项目包含基于 Playwright 的自动化测试脚本。详细测试说明请参考 `tests/README.md`。

## 浏览器兼容性

*   Chrome / Edge (最新版)
*   Firefox (最新版)
*   Safari (最新版)

## 依赖

*   [Tailwind CSS](https://tailwindcss.com/) (CDN 引入)
*   [Font Awesome](https://fontawesome.com/) (CDN 引入)
