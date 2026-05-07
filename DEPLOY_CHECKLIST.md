# 部署检查清单

## ✅ 本地已完成
- [x] Git仓库初始化
- [x] 所有代码已提交
- [x] 部署配置文件已创建（vercel.json, render.yaml）
- [x] PWA功能已实现
- [x] 界面已英文化
- [x] 移动端已适配

## 📝 需要你完成的

### 第一步：GitHub（2分钟）
- [ ] 访问 https://github.com/new
- [ ] 创建仓库 `chinglish-generator`
- [ ] 不勾选README
- [ ] 复制仓库地址

### 第二步：推送代码（1分钟）
- [ ] 在PowerShell执行：
```powershell
cd D:\12
git remote add origin https://github.com/你的用户名/chinglish-generator.git
git branch -M main
git push -u origin main
```

### 第三步：Render后端（3分钟）
- [ ] 访问 https://dashboard.render.com/
- [ ] GitHub登录
- [ ] New + → Web Service
- [ ] 选择仓库
- [ ] 配置：
  - Name: chinglish-api
  - Root Directory: backend
  - Build: `pip install -r requirements.txt`
  - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] 记下URL：https://chinglish-api.onrender.com

### 第四步：Vercel前端（2分钟）
- [ ] 访问 https://vercel.com/
- [ ] GitHub登录
- [ ] Add New → Project
- [ ] 选择仓库
- [ ] 配置：
  - Framework: Vite
  - Root: web
  - Build: `npm run build`
  - Output: dist
- [ ] 等待部署完成

### 第五步：测试（1分钟）
- [ ] 手机访问Vercel分配的域名
- [ ] 输入英文测试
- [ ] 点击Share → Add to Home Screen
- [ ] 验证PWA功能

## 🎉 全部完成！

你的网站上线地址：_______________________

你的API地址：___________________________

---

**需要帮助？随时联系我！**
