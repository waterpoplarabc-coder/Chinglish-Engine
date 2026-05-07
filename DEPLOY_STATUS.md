# 🚀 Chinglish Generator - 部署指南

## ✅ 部署状态

| 组件 | 状态 | 地址 |
|------|------|------|
| **前端 (Vercel)** | ✅ 已部署 | https://chinglish-generator.vercel.app |
| **后端 (Render)** | ⏳ 待部署 | 需要创建 |

---

## 🎯 一键部署后端到 Render

### 方法一：点击按钮部署（推荐）

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/waterpoplarabc-coder/chinglish-generator)

**点击上方按钮，然后：**
1. 使用 GitHub 账号登录 Render
2. 确认配置：
   - **Name**: `chinglish-api`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. 点击 **Deploy**
4. 等待 3-5 分钟部署完成

### 方法二：手动部署

1. 访问 https://dashboard.render.com/
2. 点击 **New +** → **Web Service**
3. 选择 `chinglish-generator` 仓库
4. 填写配置：
   - **Name**: `chinglish-api`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. 点击 **Create Web Service**
6. 等待部署完成

---

## 🔧 配置前端连接后端

部署完成后：

1. 复制你的 Render 服务地址（如 `https://chinglish-api.onrender.com`）
2. 访问 Vercel 控制台：https://vercel.com/dashboard
3. 进入 `chinglish-generator` 项目
4. 点击 **Settings** → **Environment Variables**
5. 添加变量：
   - **Name**: `VITE_API_URL`
   - **Value**: `https://chinglish-api.onrender.com`（你的Render地址）
6. 点击 **Save**
7. 重新部署：点击 **Deployments** → 最新的一次 → **Redeploy**

---

## 📱 完成！

部署完成后，用户可以通过以下地址访问：

- 🌐 **网站**: https://chinglish-generator.vercel.app
- 📖 **API文档**: https://chinglish-api.onrender.com/docs (部署后)

**手机安装为APP：**
1. 手机浏览器访问网站
2. 点击 **分享** → **添加到主屏幕**
3. 像原生APP一样使用！

---

## ⚠️ 免费版限制

| 服务 | 限制 | 说明 |
|------|------|------|
| **Render** | 15分钟无访问休眠 | 首次访问需等待10秒唤醒 |
| **Vercel** | 每月100GB流量 | 个人使用足够 |

---

## 🆘 故障排除

**问题1：前端显示 "API请求失败"**
- 检查 Render 服务是否正常运行
- 检查 Vercel 环境变量 `VITE_API_URL` 是否配置正确

**问题2：Render 部署失败**
- 检查 `backend/requirements.txt` 是否存在
- 检查 Python 版本是否为 3.12

**问题3：PWA 无法安装**
- 确保使用 HTTPS 访问
- 检查浏览器是否支持 PWA（Chrome/Safari/Edge）

---

**需要帮助？随时联系！**
