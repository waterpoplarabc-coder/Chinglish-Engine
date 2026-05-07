#!/usr/bin/env python3
"""
Render 自动部署脚本
使用 Render API 创建 Web Service
"""

import requests
import json
import base64

# Render 账号信息
RENDER_EMAIL = "waterpoplarabc@gmail.com"
RENDER_PASSWORD = "Wang2026.,./"

# API 基础 URL
RENDER_API_URL = "https://api.render.com/v1"

def get_api_key():
    """通过登录获取 API Key"""
    # Render 使用 session cookie 或 API Key
    # 这里我们需要先登录获取 session
    login_url = "https://dashboard.render.com/login"
    
    # 创建 session
    session = requests.Session()
    
    # 尝试登录
    login_data = {
        "email": RENDER_EMAIL,
        "password": RENDER_PASSWORD
    }
    
    try:
        response = session.post(login_url, json=login_data)
        if response.status_code == 200:
            print("✅ 登录成功")
            return session
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def create_web_service(session):
    """创建 Web Service"""
    
    # 服务配置
    service_config = {
        "type": "web_service",
        "name": "chinglish-api",
        "ownerId": "",  # 需要获取
        "repo": "https://github.com/waterpoplarabc-coder/chinglish-generator",
        "branch": "main",
        "rootDir": "backend",
        "runtime": "python",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
        "plan": "starter",  # 免费版
        "envVars": [
            {
                "key": "PYTHON_VERSION",
                "value": "3.12.0"
            }
        ]
    }
    
    try:
        # 获取用户/团队 ID
        user_url = f"{RENDER_API_URL}/users"
        user_response = session.get(user_url)
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"用户信息: {json.dumps(user_data, indent=2)}")
        
        # 创建服务
        services_url = f"{RENDER_API_URL}/services"
        response = session.post(services_url, json=service_config)
        
        if response.status_code in [200, 201]:
            print("✅ Web Service 创建成功!")
            service_data = response.json()
            print(json.dumps(service_data, indent=2))
            return service_data
        else:
            print(f"❌ 创建失败: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

if __name__ == "__main__":
    print("🚀 开始部署到 Render...")
    
    session = get_api_key()
    if session:
        service = create_web_service(session)
        if service:
            print("\n✅ 部署完成!")
            print(f"服务地址: {service.get('service', {}).get('url', 'N/A')}")
        else:
            print("\n❌ 部署失败，尝试手动部署...")
            print("\n手动部署步骤:")
            print("1. 访问 https://dashboard.render.com/")
            print("2. 点击 'New +' -> 'Web Service'")
            print("3. 选择 'chinglish-generator' 仓库")
            print("4. 配置:")
            print("   - Name: chinglish-api")
            print("   - Root Directory: backend")
            print("   - Build Command: pip install -r requirements.txt")
            print("   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT")
            print("5. 点击 'Create Web Service'")
    else:
        print("❌ 无法登录 Render")
