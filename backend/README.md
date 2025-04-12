# 📘 Backend API Documentation

Backend 项目统一提供 REST 和 WebSocket 接口，用于任务分发与处理。

---

## 🏷️ Task – 🎯 CAPTCHA Submission

### `POST /createTask`

**Summary:** 创建打码任务  
**Content-Type:** `application/json`  

#### 📥 Request Body:
```json
{
  "clientKey": "string",  //非必选，暂时没用
  "task": {
    "type": "AntiTurnstileTaskProxyLess", //server端只校验这个值，检验通过后task中值会原样发送给client
    "websiteURL": "https://example.com",
    "websiteKey": "site-key-value" 
  }
}
```

#### 📤 Responses:

- `200 OK`
```json
{
  "errorId": 0,
  "taskId": "uuid-string"
}
```

- `422 Validation Error`

---

### `POST /getTaskResult`

**Summary:** 获取打码结果  
**Content-Type:** `application/json`

#### 📥 Request Body:
```json
{
  "clientKey": "string",  //非必选，暂时没用
  "taskId": "uuid-string"
}
```

#### 📤 Responses:

- `200 OK`
```json
{
  "errorId": 0,
  "status": "ready",
  "solution": {
    "token": "cf-turnstile-token" //server端不会处理solution，solution中内容是client上传的
  }
}
```

- `422 Validation Error`

---

## 🏷️ REST – 📡 Worker & Task State

### `GET /api/nodes`

**Summary:** 获取所有 Worker 节点状态  

#### 📤 Response:
```json
[
  {
    "id": "worker-id",
    "ip": "192.168.1.1",
    "task_types": ["AntiTurnstileTaskProxyLess"],
    "max_concurrency": 4,
    "current_tasks": 2,
    "pending_tasks": 1,
    "connected_at": "2025-04-12 16:40:12",
    "uptime": "126 秒",
    "status": "online"
  }
]
```

---

### `GET /api/tasks`

**Summary:** 获取任务池状态  

#### 📤 Response:
```json
{
    "summary": {
        "total": 18553,
        "completed": 18333,
        "pending": 220,
        "assigned": 5
    },
    "tasks": [
        {
            "taskId": "8b7a2737-60d8-40f0-914b-7d7a91efd72c",
            "status": "processing",
            "assignedTo": "s2",
            "createdAt": "2025-04-12T09:23:34.344576",
            "type": "AntiTurnstileTaskProxyLess"
        }
    ]
}
```

---

## 🏷️ WebSocket – 🔌 节点注册与任务通信

连接地址：

```
ws://<host>/worker/{worker_id}
wss://<host>/worker/{worker_id}
```

### 支持消息类型：

| type             | 描述               | 示例字段              |
|------------------|------------------|------------------------|
| `register`       | Worker 注册        | `task_types`, `ip`    |
| `status_update`  | 主动上报当前状态（当前任务数等） | `current_tasks`       |
| `task_result`    | 返回任务执行结果         | `taskId`, `result`    |

### ✅ 示例注册请求：
```json
{
  "type": "register",
  "task_types": ["AntiTurnstileTaskProxyLess"],
  "ip": "192.168.1.10"
}
```

### ✅ 示例任务结果上报：
```json
{
  "type": "task_result",
  "taskId": "uuid-string",
  "result": {
    "token": "cf-turnstile-token"
  }
}
```

---

## 🧪 调试与开发

本地启动命令：

```bash
uvicorn main:app --reload
```
## ▶️ 一键启动服务

本地开发启动 FastAPI 服务：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Docker 启动（使用已构建镜像）：

```bash
docker run --rm -it \
  -v "$(pwd)/config.yaml:/app/config.yaml" \
  --name capsolver-client \
  hexbrewe/capsolver-client:latest
```
开发调试访问：

- Swagger UI: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc

---
