#!/bin/bash

# 前端构建脚本
echo "Building frontend..."

# 安装依赖
pnpm install

# 构建项目
pnpm build

echo "Frontend build completed. Files are in ./dist/"
echo "Ready for nginx deployment."
