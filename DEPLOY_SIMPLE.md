# 🦆 Duck Therapy 简易部署指南

## 快速部署（IP + 端口访问）

### 1. 准备工作

```bash
# 安装必要软件
sudo apt update
sudo apt install nginx nodejs npm python3 python3-pip

# 安装 pnpm 和 PM2
npm install -g pnpm pm2

# 安装 conda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

### 2. 部署后端

```bash
# 1. 进入后端目录
cd backend

# 2. 创建环境
conda create -n duck_therapy python=3.11 -y
conda activate duck_therapy

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（创建 .env 文件）
cat > .env << EOF
HOST=0.0.0.0
PORT=8000
DEBUG=false
CORS_ORIGINS=["http://localhost:3000", "http://your-server-ip"]

# 配置至少一个 LLM 提供商
OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key
# OLLAMA_BASE_URL=http://localhost:11434

LOG_LEVEL=INFO
EOF

# 5. 修改 PM2 配置文件路径
# 编辑 ecosystem.config.js，修改实际路径

# 6. 启动后端
pm2 start ecosystem.config.js
pm2 save
pm2 startup  # 设置开机自启
```

### 3. 部署前端

```bash
# 1. 回到项目根目录
cd ..

# 2. 安装依赖
pnpm install

# 3. 构建项目
pnpm build

# 4. 配置 Nginx
sudo cp nginx.conf /etc/nginx/sites-available/duck-therapy

# 修改路径为实际路径
sudo sed -i "s|/path/to/your/project|$(pwd)|g" /etc/nginx/sites-available/duck-therapy

# 启用站点
sudo ln -sf /etc/nginx/sites-available/duck-therapy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # 删除默认站点

# 测试配置
sudo nginx -t

# 启动 Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 4. 验证部署

```bash
# 检查后端状态
pm2 status
curl http://localhost:8000/health

# 检查前端
curl http://localhost/
curl http://localhost/api/health
```

### 5. 访问应用

- **前端**: `http://your-server-ip/`
- **后端API**: `http://your-server-ip/api/`
- **健康检查**: `http://your-server-ip/health`
- **API文档**: `http://your-server-ip:8000/docs` (直接访问后端)

### 6. 日常管理命令

```bash
# 后端管理
pm2 status                    # 查看状态
pm2 logs duck-therapy-backend # 查看日志
pm2 restart duck-therapy-backend # 重启
pm2 stop duck-therapy-backend    # 停止

# 前端更新
pnpm build                    # 重新构建
sudo systemctl reload nginx   # 重载 Nginx

# 系统服务
sudo systemctl status nginx   # Nginx 状态
sudo systemctl restart nginx  # 重启 Nginx
```

### 7. 故障排除

#### 后端问题
```bash
# 查看后端日志
pm2 logs duck-therapy-backend

# 手动启动测试
cd backend
conda activate duck_therapy
python main.py
```

#### 前端问题
```bash
# 检查 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log

# 检查静态文件权限
ls -la dist/

# 手动测试前端
cd dist && python3 -m http.server 3000
```

#### 网络问题
```bash
# 检查端口监听
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8000

# 检查防火墙
sudo ufw status
sudo ufw allow 80
sudo ufw allow 8000
```

### 8. 备份和恢复

```bash
# 备份配置
cp backend/.env backup/
cp nginx.conf backup/
pm2 save

# 恢复
pm2 resurrect
```
