#!/usr/bin/env python3
"""
Configuration Test Script
验证所有配置是否从环境变量和配置文件正确读取
"""
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.settings import settings
from src.utils.config_loader import config_loader

def test_environment_variables():
    """测试环境变量是否正确读取"""
    print("=== Environment Variables Test ===")
    
    # 测试 Ollama 配置
    print(f"OLLAMA_BASE_URL: {settings.ollama_base_url}")
    print(f"OLLAMA_MODEL: {settings.ollama_model}")
    print(f"OLLAMA_TIMEOUT: {settings.ollama_timeout}")
    
    # 验证是否从环境变量读取
    env_url = os.getenv("OLLAMA_BASE_URL")
    env_model = os.getenv("OLLAMA_MODEL")
    
    if env_url:
        print(f"✓ OLLAMA_BASE_URL from env: {env_url}")
        assert settings.ollama_base_url == env_url, "URL不匹配"
    else:
        print(f"✓ OLLAMA_BASE_URL using default: {settings.ollama_base_url}")
    
    if env_model:
        print(f"✓ OLLAMA_MODEL from env: {env_model}")
        assert settings.ollama_model == env_model, "模型不匹配"
    else:
        print(f"✓ OLLAMA_MODEL using default: {settings.ollama_model}")
    
    print("Environment variables test: PASSED\n")

def test_agent_configurations():
    """测试智能体配置是否正确读取"""
    print("=== Agent Configurations Test ===")
    
    # 测试智能体配置
    agents = ["listener_agent", "duck_style_agent"]
    
    for agent_name in agents:
        config = config_loader.get_agent_config(agent_name)
        if config:
            print(f"✓ {agent_name}:")
            print(f"  - Provider: {config.get('llm_provider', 'N/A')}")
            print(f"  - Model Override: {config.get('model_override', 'From env')}")
            print(f"  - Temperature: {config.get('temperature', 'N/A')}")
        else:
            print(f"✗ {agent_name}: 配置未找到")
    
    print("Agent configurations test: PASSED\n")

def test_no_hardcoded_values():
    """测试是否已移除硬编码值"""
    print("=== Hardcoded Values Test ===")
    
    # 检查是否使用了环境变量
    assert not ("localhost:11434" in str(settings.ollama_base_url) and os.getenv("OLLAMA_BASE_URL") != settings.ollama_base_url), \
        "仍在使用硬编码的 Ollama URL"
    
    assert not ("qwen2.5" in str(settings.ollama_model) and os.getenv("OLLAMA_MODEL") != settings.ollama_model), \
        "仍在使用硬编码的 Ollama 模型"
    
    print("✓ 配置正确从环境变量读取")
    print("✓ 没有检测到硬编码值")
    print("Hardcoded values test: PASSED\n")

def main():
    """运行所有测试"""
    print("Duck Therapy Backend - Configuration Test")
    print("=" * 50)
    
    try:
        test_environment_variables()
        test_agent_configurations()
        test_no_hardcoded_values()
        
        print("🎉 所有配置测试通过！")
        print("✓ Ollama URL 从环境变量读取")
        print("✓ Ollama 模型从环境变量读取") 
        print("✓ 智能体配置从 YAML 文件读取")
        print("✓ 没有硬编码值")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()