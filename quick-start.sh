#!/bin/bash

echo "🦆 Duck Therapy 快速启动"
echo "======================="

# 检查是否已经部署
if [ ! -f "backend/.env" ]; then
    echo "❌ 还没有部署，请先运行部署脚本"
    echo "请按照以下步骤操作："
    echo ""
    echo "1. 修改 backend/ecosystem.config.js 中的路径"
    echo "2. 创建 backend/.env 文件并配置 API 密钥"
    echo "3. 运行: chmod +x deploy.sh && ./deploy.sh"
    exit 1
fi

# 检查 conda 环境
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || true
conda activate duck_therapy 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Conda 环境 'duck_therapy' 不存在，请先运行部署脚本"
    exit 1
fi

# 启动后端
echo "🚀 启动后端服务..."
cd backend
pm2 start ecosystem.config.js 2>/dev/null || pm2 restart duck-therapy-backend

# 检查 nginx
echo "🌐 检查 nginx..."
sudo systemctl status nginx --no-pager -l || sudo systemctl start nginx

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 3

# 健康检查
echo "🔍 健康检查..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常，请检查日志: pm2 logs duck-therapy-backend"
fi

if curl -s http://localhost/ > /dev/null; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常，请检查 nginx 配置"
fi

# 显示访问信息
SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "🌐 服务地址:"
echo "  前端: http://$SERVER_IP/"
echo "  后端: http://$SERVER_IP:8000/"
echo "  API: http://$SERVER_IP/api/"
echo ""
echo "📋 管理命令:"
echo "  pm2 status              # 查看后端状态"
echo "  pm2 logs duck-therapy-backend  # 查看日志"
echo "  pm2 restart duck-therapy-backend  # 重启后端"
