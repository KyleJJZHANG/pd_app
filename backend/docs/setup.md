# 心理鸭后端开发环境搭建指南

## 1. 环境要求

### 1.1 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.9 或更高版本（推荐 3.11）
- **内存**: 最少 4GB，推荐 8GB+
- **存储**: 最少 2GB 可用空间

### 1.2 必需软件
- **Python 3.9+**: [官方下载](https://www.python.org/downloads/)
- **Git**: [官方下载](https://git-scm.com/downloads)
- **VS Code**: [官方下载](https://code.visualstudio.com/) （推荐）
- **Docker**: [官方下载](https://www.docker.com/get-started/) （可选，用于容器化部署）

### 1.3 可选工具
- **Postman**: API 测试工具
- **Redis**: 缓存服务（开发阶段可用内存缓存替代）
- **PostgreSQL**: 生产数据库（开发阶段使用 SQLite）

## 2. 快速开始

### 2.1 克隆项目

```bash
# 克隆项目仓库
git clone <repository-url>
cd duck-therapy-backend

# 检查项目结构
ls -la
```

### 2.2 Python 环境设置

#### 使用 conda（推荐）
```bash
# 创建 conda 环境
conda create -n duck_therapy python=3.11
conda activate duck_therapy

# 验证环境
conda info --envs
```

#### 使用 venv（可选）
```bash
# 创建虚拟环境
python -m venv duck_therapy_env

# 激活虚拟环境
# Windows
duck_therapy_env\Scripts\activate
# macOS/Linux
source duck_therapy_env/bin/activate

# 验证 Python 版本
python --version  # 应该显示 3.9+
```


### 2.3 安装依赖

```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
pip list | grep fastapi
pip list | grep crewai
```

### 2.4 环境变量配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
# Windows
notepad .env
# macOS/Linux  
nano .env
```

**必需的环境变量**：
```env
# 应用配置
APP_NAME=Duck Therapy Backend
APP_VERSION=0.1.0
DEBUG=true
LOG_LEVEL=INFO

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置（开发阶段）
DATABASE_URL=sqlite:///./duck_therapy.db

# LLM API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1

# 可选：Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 缓存配置
REDIS_URL=redis://localhost:6379/0
USE_REDIS=false  # 开发阶段设为 false

# 安全配置
SECRET_KEY=your-secret-key-here-please-change-this
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# 日志配置
LOG_FILE_PATH=./logs/app.log
```

### 2.5 数据库初始化

```bash
# 创建数据库表
python -c "
from app.database import create_tables
create_tables()
print('数据库初始化完成')
"

# 验证数据库文件
ls -la duck_therapy.db
```

### 2.6 启动开发服务器

```bash
# 启动服务器
python app.py

# 或者使用 uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 验证服务启动
curl http://localhost:8000/health
```

### 2.7 验证安装

访问以下 URL 验证服务正常运行：

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **OpenAPI 规范**: http://localhost:8000/openapi.json

## 3. 详细配置说明

### 3.1 LLM API 配置

#### OpenAI 配置
```env
# OpenAI GPT 配置
OPENAI_API_KEY=sk-...  # 从 OpenAI 获取
OPENAI_MODEL=gpt-4     # 或 gpt-3.5-turbo
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7
```

获取 OpenAI API Key：
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册账号并登录
3. 进入 API Keys 页面创建新密钥
4. 复制密钥到环境变量

#### Anthropic Claude 配置（备选）
```env
ANTHROPIC_API_KEY=sk-ant-...  # 从 Anthropic 获取
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

#### 本地 LLM 配置（高级用户）
```env
# 使用 Ollama 本地部署
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2-chinese
```

### 3.2 数据库配置

#### SQLite（开发环境，默认）
```env
DATABASE_URL=sqlite:///./duck_therapy.db
```

#### PostgreSQL（生产环境）
```env
DATABASE_URL=postgresql://username:password@localhost:5432/duck_therapy
```

安装 PostgreSQL：
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows - 从官网下载安装包
```

#### Redis 配置（可选）
```env
REDIS_URL=redis://localhost:6379/0
USE_REDIS=true
```

安装 Redis：
```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Windows - 从 GitHub 下载或使用 WSL
```

### 3.3 日志配置

```python
# 在 config/logging.py 中配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/app.log",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}
```

## 4. 开发工具配置

### 4.1 VS Code 配置

创建 `.vscode/settings.json`：
```json
{
    "python.defaultInterpreterPath": "./duck_therapy_env/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

推荐的 VS Code 扩展：
- Python
- Pylance  
- Black Formatter
- autoDocstring
- Thunder Client（API 测试）

### 4.2 Git 配置

创建 `.gitignore`：
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
duck_therapy_env/
env/
venv/

# Environment Variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite3

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini
```

### 4.3 代码质量工具

安装开发依赖：
```bash
pip install black pylint pytest pytest-asyncio httpx
```

配置 `pyproject.toml`：
```toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.pylint.messages_control]
disable = "C0330, C0326"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
asyncio_mode = "auto"
```

## 5. 项目结构创建

### 5.1 创建基础目录结构

```bash
# 创建项目目录
mkdir -p {agents,tools,models,api,config,tests,logs,data}

# 创建 __init__.py 文件
touch agents/__init__.py tools/__init__.py models/__init__.py api/__init__.py config/__init__.py

# 验证结构
tree .  # 或者 ls -la
```

### 5.2 创建基础配置文件

**requirements.txt**:
```txt
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
crewai>=0.28.8
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.13
pydantic>=2.5.0
sqlalchemy>=2.0.23
alembic>=1.13.1
redis>=5.0.1
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-dotenv>=1.0.0
loguru>=0.7.2
jieba>=0.42.1
numpy>=1.24.0
scikit-learn>=1.3.0
pytest>=7.4.3
pytest-asyncio>=0.21.1
httpx>=0.25.2
black>=23.11.0
pylint>=3.0.3
```

**app.py**（主入口文件）:
```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="Duck Therapy Backend",
    description="心理鸭多智能体后端服务",
    version="0.1.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Duck Therapy Backend is running"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
```

## 6. 测试环境验证

### 6.1 运行测试套件

```bash
# 创建测试文件
mkdir -p tests
cat > tests/test_basic.py << EOF
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_app_creation():
    assert app.title == "Duck Therapy Backend"
    assert app.version == "0.1.0"
EOF

# 运行测试
pytest tests/ -v
```

### 6.2 API 接口测试

```bash
# 测试健康检查
curl -X GET http://localhost:8000/health

# 测试 API 文档
curl -X GET http://localhost:8000/docs

# 测试 OpenAPI 规范
curl -X GET http://localhost:8000/openapi.json
```

### 6.3 环境变量测试

```python
# 创建环境变量测试脚本
cat > test_env.py << EOF
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    "OPENAI_API_KEY",
    "SECRET_KEY", 
    "DATABASE_URL"
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✓ {var}: {'*' * min(len(value), 20)}")
    else:
        print(f"✗ {var}: 未设置")

print(f"✓ Python 版本: {os.sys.version}")
print(f"✓ 工作目录: {os.getcwd()}")
EOF

python test_env.py
```

## 7. 常见问题解决

### 7.1 Python 版本问题

**问题**: `Python version 3.8 is not supported`
**解决**:
```bash
# 检查 Python 版本
python --version

# 如果版本过低，更新 Python
# Windows: 从官网下载新版本
# macOS: brew upgrade python
# Ubuntu: sudo apt update && sudo apt install python3.11
```

### 7.2 依赖安装失败

**问题**: `pip install` 失败
**解决**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 清理缓存
pip cache purge

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 7.3 环境变量问题

**问题**: 环境变量未加载
**解决**:
```bash
# 检查 .env 文件是否存在
ls -la .env

# 验证文件内容格式
cat .env | head -5

# 确保没有多余空格
sed -i 's/[[:space:]]*$//' .env  # Linux/macOS
```

### 7.4 端口占用问题

**问题**: `Address already in use`
**解决**:
```bash
# 查找占用端口的进程
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 杀死进程
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# 或者使用其他端口
uvicorn app:app --port 8001
```

### 7.5 数据库权限问题

**问题**: SQLite 权限错误
**解决**:
```bash
# 检查文件权限
ls -la duck_therapy.db

# 修改权限
chmod 664 duck_therapy.db  # Linux/macOS

# 检查目录权限
ls -la .
```

## 8. 性能优化建议

### 8.1 开发环境优化

```python
# 在 config/settings.py 中添加
DEVELOPMENT_SETTINGS = {
    "reload": True,
    "debug": True,
    "log_level": "debug",
    "workers": 1,  # 开发环境使用单进程
}

PRODUCTION_SETTINGS = {
    "reload": False,
    "debug": False,
    "log_level": "info",
    "workers": 4,  # 生产环境多进程
}
```

### 8.2 数据库连接优化

```python
# 在 database.py 中配置连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=DEBUG  # 开发环境显示 SQL
)
```

## 9. 下一步

完成基础环境搭建后，可以继续：

1. **阅读开发指南**: `docs/development.md`
2. **了解智能体设计**: `docs/agents.md`
3. **查看 API 文档**: `docs/api.md`
4. **开始编写代码**: 从简单的健康检查 API 开始
5. **运行测试**: 确保代码质量

## 10. 获取帮助

如果在搭建过程中遇到问题：

1. **检查日志**: `logs/app.log`
2. **查看 GitHub Issues**: 搜索相关问题
3. **参考官方文档**:
   - [FastAPI 文档](https://fastapi.tiangolo.com/)
   - [CrewAI 文档](https://docs.crewai.com/)
4. **联系团队**: 通过项目沟通渠道获取帮助

---

**恭喜！** 你已经成功搭建了心理鸭后端开发环境。现在可以开始进行智能体开发了！