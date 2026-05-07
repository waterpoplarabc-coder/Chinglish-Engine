# 中式多语种翻译引擎（MVP）

当前形态：规则驱动的“中文思维风格改写器”，先落地英文 → 中式英语（可控强度、可解释、可回归）。

## 快速开始（开发模式：前后端分离）

### 1) 启动后端（API）

```powershell
python -m pip install -r backend\requirements.txt
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

API 文档与健康检查：
- http://localhost:8000/docs
- http://localhost:8000/api/health

### 2) 启动前端（UI / PWA）

```powershell
cd web
npm i
npm run dev
```

打开 UI：
- http://localhost:5173/

说明：前端已配置 `/api` 代理到 `http://127.0.0.1:8000`，因此 UI 直接同源请求 `/api/rewrite`。

## 单端口部署（后端托管 UI）

```powershell
cd web
npm i
npm run build

cd ..\backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

打开：
- http://localhost:8000/（UI）
- http://localhost:8000/docs（API 文档）

PWA 说明：生产环境建议使用 HTTPS（localhost 例外），以确保 Service Worker 按预期工作。

## 回归测试

```powershell
python eval\run_regression.py
```

