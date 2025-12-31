import os
from openai import OpenAI

# 测试DeepSeek API连接
def test_deepseek_api():
    try:
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY") or "",
            base_url="https://api.deepseek.com/v1"
        )
        
        # 测试基本聊天完成
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
            temperature=0.7,
            max_tokens=100
        )
        
        print("✅ API连接成功!")
        print("响应:", response.choices[0].message.content)
        return True
    except Exception as e:
        print(f"❌ API连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_deepseek_api()