#!/bin/bash

set -e

echo "🦆 Duck Therapy 部署脚本"
echo "========================"

# 获取当前目录作为项目路径
PROJECT_DIR=$(pwd)
CONDA_ENV="duck_therapy"
NGINX_SITES_DIR="/etc/nginx/sites-available"
NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"

echo "项目路径: $PROJECT_DIR"

# 1. 后端部署
echo "📦 部署后端..."
cd $PROJECT_DIR/backend

# 激活 conda 环境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate $CONDA_ENV

# 安装/更新依赖
pip install -r requirements.txt

# 检查配置文件
python -c "from src.utils.config_loader import config_loader; print('配置验证通过')"

# 2. 前端构建
echo "🎨 构建前端..."
cd $PROJECT_DIR
pnpm install
pnpm build

# 3. 配置 Nginx
echo "⚙️  配置 Nginx..."
sudo cp nginx.conf $NGINX_SITES_DIR/duck-therapy
sudo ln -sf $NGINX_SITES_DIR/duck-therapy $NGINX_ENABLED_DIR/

# 更新 nginx 配置中的路径
sudo sed -i "s|/path/to/your/project|$PROJECT_DIR|g" $NGINX_SITES_DIR/duck-therapy

# 测试 nginx 配置
sudo nginx -t

# 4. 启动服务
echo "🚀 启动服务..."

# 更新 PM2 配置文件中的路径
cd $PROJECT_DIR/backend
sed -i "s|/path/to/your/project|$PROJECT_DIR|g" ecosystem.config.js
sed -i "s|/path/to/your/conda/envs/duck_therapy/bin/python|$(which python)|g" ecosystem.config.js

# 使用 PM2 启动后端
pm2 start ecosystem.config.js
pm2 save

# 删除默认 nginx 站点并启用我们的配置
sudo rm -f $NGINX_ENABLED_DIR/default
sudo systemctl reload nginx

# 获取服务器 IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "  前端: http://$SERVER_IP/"
echo "  后端API: http://$SERVER_IP/api/"
echo "  健康检查: http://$SERVER_IP/health"
echo "  API文档: http://$SERVER_IP:8000/docs"
echo ""
echo "📋 管理命令:"
echo "  查看后端状态: pm2 status"
echo "  查看后端日志: pm2 logs duck-therapy-backend"
echo "  重启后端: pm2 restart duck-therapy-backend"
echo "  停止后端: pm2 stop duck-therapy-backend"
echo "  重启nginx: sudo systemctl reload nginx"
