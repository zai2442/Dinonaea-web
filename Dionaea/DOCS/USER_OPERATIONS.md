# 用户管理功能接口文档 (User Operations API)

## 1. 权限说明
- 仅角色为 `Super Admin` (code: `super_admin`) 的用户可访问以下接口。
- 其他用户访问将返回 `403 Forbidden`。

## 2. 接口列表

### 2.1 创建用户 (Create User)
- **URL**: `POST /api/v1/users/`
- **描述**: 创建新用户。
- **特别说明**:
  - 如果数据库中存在相同用户名或邮箱的**软删除**记录（`deleted=True`），系统会自动执行物理删除并清理关联数据，以释放唯一索引空间，确保新用户创建成功。
- **请求体 (UserCreate)**:
  ```json
  {
    "username": "test_user",    // 必填，需唯一 (3-20字符，仅字母数字下划线)
    "email": "test@example.com",// 必填，需唯一
    "password": "password123",  // 必填，明文密码
    "status": "active",         // 可选 (active/pending，默认 active)
    "role_ids": [1]             // 可选，角色ID列表
  }
  ```
- **响应**:
  - `201 Created`: 创建成功，返回新用户对象。
  - `400 Bad Request`: 用户名或邮箱已存在（非软删除状态）。

### 2.3 更新用户 (Update User)
- **URL**: `PUT /api/v1/users/{user_id}`
- **描述**: 更新用户信息，支持乐观锁。
- **保护机制**: 用户名为 `admin` 的内置管理员不可修改。
- **请求体 (UserUpdate)**:
  ```json
  {
    "username": "new_username", // 可选，需唯一 (3-20字符，仅字母数字下划线)
    "email": "new@example.com", // 可选，需唯一
    "status": "active",         // 可选 (active/pending)
    "role_ids": [1, 2],         // 可选，角色ID列表
    "version": 1                // 必填，当前版本号 (乐观锁)
  }
  ```
- **响应**:
  - `200 OK`: 更新成功，返回更新后的用户对象。
  - `400 Bad Request`: 参数错误（如用户名重复、邮箱重复、格式错误）。
  - `403 Forbidden`: 权限不足。
  - `404 Not Found`: 用户不存在。
  - `409 Conflict`: 数据版本冲突（已被他人修改），请刷新后重试。

### 2.4 删除用户 (Delete User)
- **URL**: `DELETE /api/v1/users/{user_id}`
- **描述**: 永久删除用户及其关联数据（角色、日志、会话）。
- **保护机制**: 用户名为 `admin` 的内置管理员不可删除。
- **响应**:
  - `204 No Content`: 删除成功。
  - `403 Forbidden`: 权限不足。
  - `404 Not Found`: 用户不存在。

## 3. 错误码对照表

| HTTP Code | 错误信息 (Detail) | 说明 |
|-----------|-------------------|------|
| 400 | Username already registered | 用户名已存在 |
| 400 | Email already registered | 邮箱已存在 |
| 403 | Only Super Admin can perform this action | 权限不足 |
| 404 | User not found | 用户不存在 |
| 409 | Conflict: Data has been modified by another user | 乐观锁冲突 |
| 422 | Validation Error | 字段格式校验失败 |

## 4. 前端交互逻辑
- **新增**:
  1. 点击列表右上角 "新增用户" 按钮（仅 Super Admin 可见）。
  2. 弹窗输入信息，默认角色为 User。
  3. 提交 POST 请求。
  4. 成功后刷新列表。
- **编辑**:
  1. 点击编辑按钮，获取用户详情 (包含当前 version)。
  2. 弹窗显示表单，验证输入格式。
  3. 提交 PUT 请求。
  4. 如果返回 409，提示用户刷新。
  5. 成功后刷新列表并显示 Toast。
  6. **保护**: 如果是 `admin` 用户，按钮替换为 "系统锁定" 标签。
- **删除**:
  1. 点击删除按钮，弹窗警告。
  2. 确认后提交 DELETE 请求。
  3. 成功后刷新列表。
  4. **保护**: 如果是 `admin` 用户，按钮替换为 "系统锁定" 标签。
