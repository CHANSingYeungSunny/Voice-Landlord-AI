# 最终测试：验证DeepSeek API配置
import os
from openai import OpenAI

# 测试配置
API_KEY = os.getenv("API_KEY") or ""
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

print("=== DeepSeek API配置测试 ===")
print(f"API密钥: {'已配置' if API_KEY else '未配置'}")
print(f"基础URL: {BASE_URL}")
print(f"模型: {MODEL}")

# 测试API连接
try:
    print("\n正在尝试连接API...")
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    
    # 创建一个简单的测试请求
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Hello, please reply with 'API connected successfully'"}],
        temperature=0.0,
        max_tokens=50
    )
    
    print("✅ API调用成功!")
    print("响应内容:", response.choices[0].message.content)
    
except Exception as e:
    print(f"❌ API调用失败: {str(e)}")
    print("\n可能的原因:")
    print("1. API密钥无效或已过期")
    print("2. API密钥格式不正确")
    print("3. DeepSeek API服务可能暂时不可用")
    print("4. 网络连接问题")
    print("\n建议:")
    print("- 检查API密钥是否正确")
    print("- 确认DeepSeek账户状态是否正常")
    print("- 访问DeepSeek官方平台验证API密钥")