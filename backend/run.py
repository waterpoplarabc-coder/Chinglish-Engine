"""启动入口 - 从项目根目录运行后端，支持同时 serve 前端 dist"""
import uvicorn
import sys
from pathlib import Path

# 确保能找到 backend 包
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
