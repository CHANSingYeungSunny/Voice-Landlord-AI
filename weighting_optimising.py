import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI

class DeepSeekClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        # 硬编码API密钥，与landlord_agent保持一致
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or ""
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        if not self.api_key:
            raise ValueError("请提供DeepSeek API密钥")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(self, messages: List[Dict[str, str]], 
             model: str = "deepseek-reasoner",
             temperature: float = 0.7,
             max_tokens: int = 2000) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")
    
    def get_card_recommendation(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": "你是一个专业的斗地主AI助手。你需要分析当前牌局情况，根据规则和历史数据做出最优出牌决策。"},
            {"role": "user", "content": prompt}
        ]
        return self.chat(messages)
    
    def process_voice_input(self, voice_text: str) -> Dict[str, Any]:
        """处理人类语音输入，提取玩家、回合、牌和权重信息"""
        system_prompt = """你是一个智能语音解析助手，专门处理斗地主游戏的语音指令。
请将人类语音输入（如"A2 出 J"）解析为结构化的游戏记录，包含以下字段：
1. player: 玩家标识（字符串格式，如"A2"）
2. round: 当前回合数（整数格式，根据上下文推断或默认1）
3. card: 出的牌（字符串格式，如"heart J"或"spade J"等标准格式）
4. weighting: 权重值（浮点数格式，范围0-1，根据牌的重要性和局势推断，默认0.8）

输出必须是严格的JSON格式，只包含这四个字段，不包含任何其他解释或说明。
例如：
输入："A2 出 J"
输出：{"player": "A2", "round": 1, "card": "heart J", "weighting": 0.8}

输入："玩家B在第三回合出了黑桃A"
输出：{"player": "B", "round": 3, "card": "spade A", "weighting": 0.95}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": voice_text}
        ]
        
        try:
            response = self.chat(messages)
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise Exception(f"AI返回格式错误: {str(e)}")
        except Exception as e:
            raise Exception(f"处理语音输入失败: {str(e)}")

# Import CardDB for demonstration
from card_db import CardDB

if __name__ == "__main__":
    try:
        client = DeepSeekClient()
        
        # 示例1: 处理简单的语音输入
        voice_input1 = "A2 出 J"
        print(f"\n处理语音输入: {voice_input1}")
        record1 = client.process_voice_input(voice_input1)
        print(f"解析结果: {json.dumps(record1, ensure_ascii=False, indent=2)}")
        
        # 示例2: 处理更复杂的语音输入
        voice_input2 = "玩家B在第三回合出了黑桃A"
        print(f"\n处理语音输入: {voice_input2}")
        record2 = client.process_voice_input(voice_input2)
        print(f"解析结果: {json.dumps(record2, ensure_ascii=False, indent=2)}")
        
        # 示例3: 演示与数据库的集成
        print(f"\n将解析结果保存到数据库...")
        db = CardDB()
        db.add(record1['player'], record1['round'], record1['card'], record1['weighting'])
        db.add(record2['player'], record2['round'], record2['card'], record2['weighting'])
        print(f"数据库内容:")
        print(db.get_all())
        
        # 清空数据库以便测试
        db.clear()
        
    except ValueError as e:
        print(f"配置错误: {e}")
    except Exception as e:
        print(f"错误: {e}")