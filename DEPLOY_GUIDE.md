# 🚀 Chinglish Generator 部署指南

## ✅ 本地准备已完成

Git仓库已创建并提交，位置：`D:\12`

---

## 📝 你需要完成的3个步骤

### 步骤1：创建GitHub仓库（2分钟）

1. 打开 https://github.com/new
2. 输入仓库名：`chinglish-generator`
3. **不要勾选** "Initialize this repository with a README"
4. 点击 **Create repository**
5. 复制仓库地址（类似：`https://github.com/你的用户名/chinglish-generator.git`）

---

### 步骤2：推送代码到GitHub（1分钟）

在PowerShell中执行：

```powershell
cd D:\12
git remote add origin https://github.com/你的用户名/chinglish-generator.git
git branch -M main
git push -u origin main
```

输入你的GitHub用户名和密码（或Token）。

---

### 步骤3：部署到Render（后端，3分钟）

1. 打开 https://dashboard.render.com/
2. 用GitHub账号登录
3. 点击 **New +** → **Web Service**
4. 选择你的 `chinglish-generator` 仓库
5. 配置：
   - **Name**: `chinglish-api`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. 点击 **Create Web Service**
7. 等待部署完成（约3分钟），记下URL：`https://chinglish-api.onrender.com`

---

### 步骤4：部署到Vercel（前端，2分钟）

1. 打开 https://vercel.com/
2. 用GitHub账号登录
3. 点击 **Add New...** → **Project**
4. 选择 `chinglish-generator` 仓库
5. 配置：
   - **Framework Preset**: Vite
   - **Root Directory**: `web`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. 点击 **Deploy**
7. 等待部署完成，访问分配的域名

---

### 步骤5：配置API代理（1分钟）

1. 在Vercel控制台，进入你的项目
2. 点击 **Settings** → **Environment Variables**
3. 添加变量：
   - Name: `VITE_API_URL`
   - Value: `https://chinglish-api.onrender.com`（你的Render地址）
4. 点击 **Save**
5. 重新部署：点击 **Deployments** → 最新的一次 → **Redeploy**

---

## 🎉 完成！

访问你的PWA应用：`https://chinglish-generator-xxx.vercel.app`

手机访问 → 点击"Share" → "Add to Home Screen"即可安装！

---

## 📱 用户安装指南（给你的用户）

```
1. 手机浏览器访问：https://chinglish-generator-xxx.vercel.app
2. 点击浏览器菜单（Share/分享）
3. 选择"Add to Home Screen"（添加到主屏幕）
4. 像原生APP一样使用！
```

---

## ⚠️ 免费版限制

| 服务 | 限制 | 解决方案 |
|------|------|----------|
| Render | 15分钟无访问会休眠 | 首次访问需等待10秒唤醒 |
| Vercel | 每月100GB流量 | 个人使用足够 |

如需保持Render一直唤醒，可用UptimeRobot每5分钟ping一次。

---

## 🔧 故障排除

**问题1：Git推送失败**
```
解决方案：使用GitHub Token代替密码
1. https://github.com/settings/tokens 生成Token
2. 推送时输入Token作为密码
```

**问题2：Render部署失败**
```
检查：
- Root Directory是否正确设置为backend
- requirements.txt是否存在
- Python版本是否为3.12
```

**问题3：Vercel部署失败**
```
检查：
- Root Directory是否正确设置为web
- dist目录是否存在（应已存在）
```

---

## 💡 后续优化（可选）

1. **绑定自定义域名**：Vercel设置中添加自己的域名
2. **Google Analytics**：添加访问统计
3. **SEO优化**：添加meta标签、sitemap

---

**遇到问题随时喊我！**
