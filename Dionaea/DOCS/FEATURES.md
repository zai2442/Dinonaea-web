# 功能实现说明 (Feature Implementation)

## 1. 后端 API (FastAPI)
- **日志查询 (`GET /api/v1/data/logs`)**:
  - 支持分页 (`skip`, `limit`)
  - 支持多维度筛选: 时间范围 (`start_time`, `end_time`), 源IP (`source_ip`), 用户名 (`username`), 密码 (`password`)
  - 返回字段包含: 时间戳, 源IP, 目标端口, 用户名, 密码, 协议, 连接状态, 传感器名称

- **统计图表 (`GET /api/v1/data/stats/charts`)**:
  - 返回 ECharts 所需的聚合数据
  - **Redis 缓存**: 结果缓存 10 分钟，减少数据库压力

- **统计摘要 (`GET /api/v1/data/stats/summary`)**:
  - 返回最频繁的攻击指标 (IP, User, Password)
  - 兼容 `Login_statistics.sh` 的逻辑

- **缓存刷新 (`POST /api/v1/data/refresh`)**:
  - 强制刷新 Redis 缓存
  - 由 `Check.sh` 脚本在检测到日志变更时触发

## 2. 数据库设计
- **表名**: `attack_logs`
- **字段**:
  - `timestamp`: 攻击时间 (索引)
  - `source_ip`: 源 IP (索引)
  - `username`: 尝试用户名 (索引)
  - `password`: 尝试密码
  - `target_port`: 目标端口
  - `protocol`: 协议 (smb, ftp, etc.)
  - `connection_status`: 连接状态
  - `sensor_name`: 传感器标识

## 3. 前端仪表盘
- **技术栈**: 原生 JS + Tailwind CSS + ECharts
- **模块**:
  - **实时日志表格**: 支持翻页，显示详细攻击记录。
  - **可视化图表**:
    - 柱状图: 攻击源 IP 分布
    - 饼图: 用户名分布
    - 词云: 密码字典分布
  - **联动刷新**: 自动获取最新统计摘要。

## 4. 性能优化
- **后端**: 使用 Redis 缓存高频统计查询。
- **前端**: 使用分页加载日志数据，避免一次性渲染大量 DOM。
- **并发**: 经过初步测试，API 可处理并发请求 (需根据实际硬件调整 Worker 数量)。

## 5. 安全性
- **认证**: 所有数据接口需 JWT Token (`Authorization: Bearer ...`)。
- **权限**: 依赖 `get_current_active_user` 确保用户状态正常。
