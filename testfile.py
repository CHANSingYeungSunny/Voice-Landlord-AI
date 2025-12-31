import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI

# ====== 1. 把系统提示单独放在常量里 ======
SYSTEM_PROMPT = """
你是“斗地主( Dou Dizhu )”的博弈论决策引擎，不是聊天机器人。请在不确定信息下做稳健决策：地主 vs 两名农民(协作阵营)的对抗博弈。[规则优先]

### 1) 任务
输入会给出：你的身份(地主/农民)、你的手牌、当前轮到谁、桌面待跟牌(last_play)、历史出牌与可能的剩余牌推断信息(可为空)。
你要输出“下一手建议出牌”，并给出可验证的理由与风险评估。

### 2) 强制流程（必须按顺序做）
A. 解析输入，检查信息完整性；缺信息先在 assumptions 字段列出最小假设。
B. 枚举你当前所有“合法走法”(legal_moves)，并标注每个走法的牌型(type)与强度(rank)。
C. 做博弈论评估：
   - 阵营结构：地主=单人最大化胜率；农民=两人协作最大化“农民阵营胜率”(允许牺牲局部收益帮助队友走牌)。
   - 目标函数：优先“保证胜率/避免必败”，其次“加速走牌/控制节奏”，最后“争取更高收益”。
   - 风险控制：保留关键资源（尤其是能打断对手节奏的强牌，如炸弹/火箭等），除非立即形成必胜或避免必败。
   - 不完全信息：对未知牌使用保守推断；把对手可能持有的关键反制牌当作高概率风险进行最坏情况评估(近似 minimax)。
D. 选择 recommended_move，并说明为什么它在最坏情况下更稳健；同时给出 1 个备选 move。

### 3) 规则约束（简化但要一致）
- 必须跟同类牌型且更大才能压制 last_play；否则可选择 Pass。
- 炸弹(四张同点)可压任何非火箭组合；火箭(双王)压制一切。
- 顺子/连对/飞机等必须长度匹配才能互压；2 和王不能参与顺子。(如果输入声明的规则不同，以输入为准)
若输入规则与上述冲突，以输入规则为准，并在 assumptions 说明。

### 4) 输出格式（只输出 JSON，不要输出多余文字）
{
  "recommended_move": {"action": "play|pass", "cards": ["..."], "type": "..."},
  "backup_move": {"action": "play|pass", "cards": ["..."], "type": "..."},
  "assumptions": ["..."],
  "legal_moves_count": 0,
  "reasoning": [
    "一句话理由1(博弈论/阵营协作/节奏控制/资源保留/最坏情况)",
    "一句话理由2"
  ],
  "risk_notes": ["该走法可能被哪些牌型反制/可能导致的坏后果"]
}
"""

class DeepSeekClient:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        if not self.api_key:
            raise ValueError("请提供DeepSeek API密钥")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(self, messages: List[Dict[str, str]], 
             model: str = "deepseek-reasoner",
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
            raise Exception(f"DeepSeek API调用失败: {str(e)}")
    
    def get_card_recommendation(self, state: Dict[str, Any]) -> str:
        user_prompt = json.dumps(state, ensure_ascii=False)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        return self.chat(messages)

if __name__ == "__main__":
    try:
        client = DeepSeekClient()
        # ✅ 构造一个完整的测试局面（后续从数据库/摄像头/语音模块获取）
        test_state = {
            "元信息": {
                "游戏": "斗地主",
                "版本": "prompt_v1.0",
                "语言": "zh-CN",
                "输出要求": "只输出JSON（不要Markdown、不要多余文字）"
            },
            "规则": {
                "牌面大小(从大到小)": ["大王", "小王", "2", "A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3"],
                "跟牌规则": "必须同牌型且更大才能压制上一手，否则可Pass",
                "火箭": "王炸（大小王）压制一切",
                "炸弹": "四张同点数可压制任何非火箭牌型",
                "顺子相关": "2和王不能参与顺子"
            },
            "玩家与阵营": [
                {"座位": "A", "阵营": "地主"},
                {"座位": "B", "阵营": "农民"},
                {"座位": "C", "阵营": "农民"}
            ],
            "局面": {
                "我的座位": "B",
                "我的阵营": "农民",
                "轮到谁": "B",
                "阶段": "出牌",
                "桌面待跟牌(last_play)": {
                    "是否存在": True,
                    "出牌者": "A",
                    "牌型": "对子",
                    "牌": ["9", "9"],
                    "关键强度点": "9",
                    "张数": 2
                },
                "历史出牌": [
                    {"回合": 1, "玩家": "A", "动作": "出牌", "牌型": "单张", "牌": ["K"]},
                    {"回合": 2, "玩家": "B", "动作": "出牌", "牌型": "单张", "牌": ["A"]},
                    {"回合": 3, "玩家": "C", "动作": "Pass", "牌型": "Pass", "牌": []},
                    {"回合": 4, "玩家": "A", "动作": "出牌", "牌型": "对子", "牌": ["9", "9"]}
                ],
                "我的手牌": {
                    "表示格式": "仅点数不含花色",
                    "牌": ["3","3","4","5","6","6","7","8","8","10","J","Q","K","A","2","小王"],
                    "张数": 16
                },
                "对手剩余张数": {
                    "A": 12,
                    "C": 15
                },
                "不完全信息推断设置": {
                    "策略": "保守（偏最坏情况/近似minimax）",
                    "默认高风险牌假设可能存在": ["大王", "小王", "2", "炸弹"]
                }
            },
            "任务": {
                "目标": "最大化农民阵营胜率（允许为队友铺路/牺牲局部收益）"
            }
        }
        result = client.get_card_recommendation(test_state)
        print("=== 模型输出 ===")
        print(result)

        # 可选：尝试解析JSON验证格式
        try:
            parsed = json.loads(result)
            print("\n=== 解析成功 ===")
            print(f"推荐动作: {parsed.get('recommended_move')}")
            print(f"备选动作: {parsed.get('backup_move')}")
        except json.JSONDecodeError as e:
            print(f"\n⚠️ JSON解析失败: {e}")

    except ValueError as e:
        print(f"配置错误: {e}")
    except Exception as e:
        print(f"错误: {e}")