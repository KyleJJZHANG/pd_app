module.exports = {
  apps: [{
    name: 'duck-therapy-backend',
    script: 'uvicorn',
    args: 'main:app --host 0.0.0.0 --port 8000',
    cwd: '/path/to/your/project/backend',
    interpreter: '/path/to/your/conda/envs/duck_therapy/bin/python',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '/path/to/your/project/backend',
      // 添加你的环境变量
      OPENAI_API_KEY: 'your-openai-key',
      ANTHROPIC_API_KEY: 'your-anthropic-key',
      OLLAMA_BASE_URL: 'http://localhost:11434'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
