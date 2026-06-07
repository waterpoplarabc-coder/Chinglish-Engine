FROM python:3.12-slim AS backend

WORKDIR /app

# 安装后端依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY backend/ ./backend/
COPY rulepacks/ ./rulepacks/

# 构建前端
FROM node:20-alpine AS frontend
WORKDIR /app
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ .
RUN npm run build

# 最终镜像
FROM python:3.12-slim
WORKDIR /app
COPY --from=backend /app/backend/ ./backend/
COPY --from=backend /app/rulepacks/ ./rulepacks/
COPY --from=frontend /app/dist/ ./web/dist/

# 运行时依赖
RUN pip install --no-cache-dir fastapi uvicorn pydantic python-multipart starlette anyio

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
