import json
import os
from pathlib import Path
from qwen_client import QwenClient
from database import CardDB

LANDLORD_RULES = """
斗地主游戏规则：
1. 牌型：单张、对子、顺子、连对、飞机、飞机带翅膀、四带二、炸弹
2. 大小：大王>小王>2>A>K>Q>J>10>...>3
3. 炸弹可以炸任何非炸弹的牌型
4. 每轮必须出比上一手牌更大的相同牌型
"""

class LandlordAgent:
    def __init__(self, api_key: str = None, db_path: str = None):
        self.qwen = QwenClient(api_key)
        self.db = CardDB(db_path)
        self.current_hand = []
        self.current_round = 0
        self.prev_card = None
        self.current_role = "农民"
    
    def record(self, player: str, round: int, card: str, weighting: float = 1.0):
        self.db.add(player, round, card, weighting)
    
    def record_batch(self, records: list):
        self.db.add_batch(records)
    
    def set_hand(self, hand: list, round: int, prev_card: str = None, role: str = "农民"):
        self.current_hand = hand
        self.current_round = round
        self.prev_card = prev_card
        self.current_role = role
    
    def decide(self) -> str:
        # 获取历史数据
        history_records_json = self.db.get_all()
        
        # 将JSON字符串转换为Python列表
        history_records = json.loads(history_records_json) if history_records_json else []
        
        # 将历史数据转换为结构化格式
        history_plays = []
        if history_records:
            for record in history_records:
                # 从字典中提取信息
                player = record.get('player', '')
                round_num = record.get('round', 1)
                card = record.get('card', '')
                
                # 提取牌的点数（去掉花色）
                rank = card.split()[-1] if card and card != '无' else ''
                
                history_plays.append({
                    "回合": int(round_num),
                    "玩家": player,
                    "动作": "出牌" if card and card != '无' else "Pass",
                    "牌型": "单张" if card and card != '无' else "Pass",
                    "牌": [rank] if card and card != '无' else []
                })
        
        # 构建结构化游戏状态
        game_state = {
            "元信息": {
                "游戏": "斗地主",
                "版本": "prompt_v1.0",
                "语言": "zh-CN",
                "输出要求": "只输出JSON（不要Markdown、不要多余文字）"
            },
            "规则": {
                "牌面大小(从大到小)": ["大王", "小王", "2", "A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3"],
                "跟牌规则": "当桌面有待跟牌时，如果手中有同牌型且更大的牌，必须跟牌压制上一手；只有当没有能压制的牌时，才能选择Pass",
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
                "我的座位": "A" if self.current_role == "地主" else "B",
                "我的阵营": self.current_role,
                "轮到谁": "A" if self.current_role == "地主" else "B",  # 确保轮到谁与我的座位一致
                "阶段": "出牌",
                "桌面待跟牌(last_play)": {
                    "是否存在": True if self.prev_card and self.prev_card != '无' else False,
                    "出牌者": "B" if self.current_role == "地主" else "A",
                    "牌型": "单张" if self.prev_card and self.prev_card != '无' else "无",
                    "牌": [self.prev_card.split()[-1]] if self.prev_card and self.prev_card != '无' else [],
                    "关键强度点": self.prev_card.split()[-1] if self.prev_card and self.prev_card != '无' else "",
                    "张数": 1 if self.prev_card and self.prev_card != '无' else 0,
                    "当前状态": "必须首发出牌，绝对不能选择Pass" if not (self.prev_card and self.prev_card != '无') else "必须跟牌，手牌中有比上一手更大的牌时绝对不能Pass",
                    "提示信息": "根据规则，当你有能压制上一手牌的牌时，必须出牌压制，不能选择Pass。请严格遵循牌面大小规则：大王>小王>2>A>K>Q>J>10>9>8>7>6>5>4>3"
                },
                "历史出牌": history_plays,
                "我的手牌": {
                    "表示格式": "仅点数不含花色",
                    "牌": self.current_hand,
                    "张数": len(self.current_hand)
                },
                "对手剩余张数": {
                    "B": 15,  # 假设值，实际应用中需要跟踪
                    "C": 15   # 假设值，实际应用中需要跟踪
                } if self.current_role == "地主" else {
                    "A": 12,  # 假设值，实际应用中需要跟踪
                    "C": 15   # 假设值，实际应用中需要跟踪
                },
                "不完全信息推断设置": {
                    "策略": "保守（偏最坏情况/近似minimax）",
                    "默认高风险牌假设可能存在": ["大王", "小王", "2", "炸弹"]
                }
            },
            "任务": {
                "目标": "最大化地主胜率" if self.current_role == "地主" else "最大化农民阵营胜率（允许为队友铺路/牺牲局部收益）"
            }
        }
        
        # 获取推荐
        response_str = self.qwen.get_card_recommendation(game_state)
        
        try:
            # 解析JSON响应
            response = json.loads(response_str)
            return response
        except json.JSONDecodeError:
            # 如果JSON解析失败，返回原始字符串
            return response_str

def main():
    agent = LandlordAgent(api_key=os.getenv("QWEN_API_KEY") or "")
    
    print("=== 斗地主AI (Qwen-Turbo) ===")
    print("指令：")
    print("  1. 输入手牌，进入决策模式")
    print("     格式：手牌 轮数 上一手牌 角色")
    print("     示例：3,4,5,6,7 2 heart 8 地主")
    print("  2. record 玩家 轮数 牌 权重    - 写入历史数据")
    print("  3. show                       - 显示所有记录")
    print("  4. clear                      - 清空数据库")
    print("  5. quit                       - 退出\n")
    
    while True:
        try:
            cmd = input("> ").strip()
            if not cmd:
                continue
                
            parts = cmd.split()
            
            if parts[0] == "quit":
                break
                
            elif parts[0] == "show":
                print(agent.db.get_all())
                
            elif parts[0] == "clear":
                agent.db.clear()
                print("已清空\n")
                
            elif parts[0] == "record":
                if len(parts) >= 4:
                    player = parts[1]
                    round_num = int(parts[2])
                    card = parts[3]
                    weighting = float(parts[4]) if len(parts) > 4 else 1.0
                    agent.record(player, round_num, card, weighting)
                    print(f"已记录：{player} 第{round_num}轮 {card}\n")
                else:
                    print("用法：record 玩家 轮数 牌 权重\n")
                    
            else:
                hand_str = parts[0]
                round_num = int(parts[1]) if len(parts) > 1 else 1
                prev = parts[2] if len(parts) > 2 else None
                role = parts[3] if len(parts) > 3 else "农民"
                
                hand = hand_str.split(',')
                
                print(f"\n手牌：{', '.join(hand)}")
                print(f"轮数：{round_num}")
                print(f"上一手牌：{prev or '无'}")
                print(f"角色：{role}")
                print("\n思考中...")
                
                result = agent.decide()
                
                print("\n决策结果：")
                if isinstance(result, dict):
                    # 格式化显示JSON响应
                    recommended = result.get('recommended_move', {})
                    backup = result.get('backup_move', {})
                    reasoning = result.get('reasoning', [])
                    risk_notes = result.get('risk_notes', [])
                    
                    print(f"推荐出牌：{recommended.get('action', '未知')}")
                    if recommended.get('cards'):
                        print(f"牌型：{recommended.get('type', '未知')}")
                        print(f"具体牌：{', '.join(recommended.get('cards', []))}")
                    
                    if backup.get('cards') and backup != recommended:
                        print(f"\n备选出牌：{backup.get('action', '未知')}")
                        print(f"牌型：{backup.get('type', '未知')}")
                        print(f"具体牌：{', '.join(backup.get('cards', []))}")
                    
                    if reasoning:
                        print("\n决策理由：")
                        for i, reason in enumerate(reasoning, 1):
                            print(f"  {i}. {reason}")
                    
                    if risk_notes:
                        print("\n风险提示：")
                        for i, note in enumerate(risk_notes, 1):
                            print(f"  {i}. {note}")
                else:
                    # 如果不是字典，显示原始结果
                    print(f"{result}")
                print()
                    
        except Exception as e:
            print(f"错误：{e}\n")

if __name__ == "__main__":
    main()
