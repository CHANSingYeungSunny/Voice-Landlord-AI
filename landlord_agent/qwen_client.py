import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI

# ====== 1. 把系统提示单独放在常量里 ======
SYSTEM_PROMPT = """
你是斗地主游戏的出牌决策工具。

### 任务
根据输入的游戏状态（身份、手牌、当前轮到谁、桌面待跟牌、历史出牌等），仅输出下一手建议出牌的具体数据。

### 规则约束
- **首发出牌规则（强制）：当桌面没有待跟牌时，你必须出牌，绝对不能选择 Pass。只要你手中有牌，无论牌的大小，都必须从手牌中选择合适的牌型出牌。**
- **跟牌规则（强制）：当桌面有待跟牌时，如果手中有同牌型且更大的牌，必须跟牌压制上一手；只有当手中确实没有能压制的牌时，才能选择 Pass。**
- **牌面大小规则（单张）：大王>小王>2>A>K>Q>J>10>9>8>7>6>5>4>3**
- **关键说明（单张牌）：
  - 如果对方出K，你手牌中有A或2，必须出A或2，绝对不能Pass。
  - 如果对方出A，你手牌中有2，必须出2，绝对不能Pass。
  - 你必须严格按照牌面大小规则进行比较。
  - **如果桌面没有待跟牌（即你是首发出牌），你必须出牌，不能选择Pass，无论你手中的牌是什么。**
  - **例如：如果你的手牌是["K"]，且桌面没有待跟牌，你必须出K，绝对不能Pass。**
- 炸弹(四张同点)可压任何非火箭组合；火箭(双王)压制一切。
- 顺子/连对/飞机等必须长度匹配才能互压；2 和王不能参与顺子。

### 输出格式
仅输出严格的JSON格式数据，包含推荐出牌信息和完整的推理链条，不添加任何其他内容：
{
  "recommended_move": {
    "action": "play|pass", 
    "cards": [...], 
    "type": "..."
  },
  "reasoning": [
    "第一步推理...",
    "第二步推理...",
    "第三步推理..."
  ]
}
"""

QWEN_API_KEY = os.getenv("QWEN_API_KEY") or ""
class QwenClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("QWEN_API_KEY") or QWEN_API_KEY
        self.base_url = base_url or os.getenv("QWEN_BASE_URL") or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        
        if not self.api_key:
            raise ValueError("请提供Qwen API密钥")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(self, messages: List[Dict[str, str]], 
             model: str = "qwen-turbo",
             temperature: float = 0.2,
             max_tokens: int = 2000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Qwen API调用失败: {str(e)}")
    
    def get_card_recommendation(self, state: Dict[str, Any]) -> str:
        user_prompt = json.dumps(state, ensure_ascii=False)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        return self.chat(messages)

if __name__ == "__main__":
    try:
        client = QwenClient()
        result = client.get_card_recommendation({"test": "message"})
        print(result)
    except ValueError as e:
        print(f"配置错误: {e}")
    except Exception as e:
        print(f"错误: {e}")
