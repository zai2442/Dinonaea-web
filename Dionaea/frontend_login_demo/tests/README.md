# 自动化测试说明

本项目使用 [Playwright](https://playwright.dev/python/) 进行端到端 (E2E) 测试。

## 环境准备

1.  **创建虚拟环境** (推荐，避免全局污染):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **安装 Playwright**:
    ```bash
    pip install playwright
    playwright install chromium
    ```

## 运行测试

测试脚本 `test_login.py` 会启动浏览器并模拟用户交互流程。

1.  **启动本地服务器**:
    在项目根目录 (`frontend_login_demo`) 下运行:
    ```bash
    python3 -m http.server 8000 &
    ```

2.  **运行测试**:
    ```bash
    python3 tests/test_login.py
    ```

## 测试覆盖范围

*   页面加载与标题检查。
*   表单元素存在性检查。
*   输入框必填验证。
*   Mock 登录流程 (输入 admin/password 并验证成功提示)。
