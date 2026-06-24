from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response
from pathlib import Path

from app.api.rewrite import router as rewrite_router


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _dist_dir() -> Path:
    return _repo_root() / "web" / "dist"


def _cache_control(path: str) -> str:
    path = path.lstrip("/")
    if path.startswith("assets/"):
        return "public, max-age=31536000, immutable"
    if path.endswith(".html") or path in {"manifest.webmanifest", "sw.js"} or path.startswith("workbox-") or path.startswith(
        "registerSW"
    ):
        return "no-cache"
    return "public, max-age=3600"


def create_app() -> FastAPI:
    app = FastAPI(title="zh-style translation engine", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(rewrite_router)

    @app.get("/", response_class=HTMLResponse)
    def index():
        dist = _dist_dir()
        index_path = dist / "index.html"
        if index_path.exists():
            return FileResponse(
                index_path,
                media_type="text/html",
                headers={"Cache-Control": "no-cache"},
            )
        return """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>中式多语种引擎 API</title>
    <style>
      body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;max-width:880px;margin:40px auto;padding:0 16px;line-height:1.6}
      code,pre{background:#f1f5f9;border:1px solid #e2e8f0;border-radius:8px;padding:2px 6px}
      pre{padding:12px;overflow:auto}
      a{color:#0284c7;text-decoration:none}
      a:hover{text-decoration:underline}
    </style>
  </head>
  <body>
    <h1>中式多语种引擎 API</h1>
    <p>服务已启动。常用入口：</p>
    <ul>
      <li><a href="/docs">/docs</a>（交互式接口文档）</li>
      <li><a href="/api/health">/api/health</a>（健康检查）</li>
    </ul>
    <h2>/api/rewrite 示例</h2>
    <pre><code>POST /api/rewrite
Content-Type: application/json

{"text":"Please turn on the light.","lang":"en","level":5,"domain":"default","seed":2,"explain":true}</code></pre>
  </body>
</html>"""

    @app.get("/api/health")
    def health():
        return {"ok": True, "version": "2.0"}

    @app.get("/api/version")
    def version():
        return {"version": "2.0", "engine": "chinglish", "features": ["L5_strip", "third_person", "compound_sentences", "ui_v2"]}

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str) -> Response:
        dist = _dist_dir()
        index_path = dist / "index.html"
        if not index_path.exists():
            return HTMLResponse(content="Not Found", status_code=404)

        safe_path = (dist / full_path).resolve()
        if dist.resolve() in safe_path.parents and safe_path.exists() and safe_path.is_file():
            return FileResponse(
                safe_path,
                headers={"Cache-Control": _cache_control(full_path)},
            )

        return FileResponse(
            index_path,
            media_type="text/html",
            headers={"Cache-Control": "no-cache"},
        )

    return app


app = create_app()
