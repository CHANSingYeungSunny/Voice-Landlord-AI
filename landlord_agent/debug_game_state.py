#!/usr/bin/env python3
"""
调试脚本：查看发送给AI的完整游戏状态
"""

import sys
import os
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from landlord_agent import LandlordAgent

def debug_game_state():
    """调试游戏状态"""
    print("=== 游戏状态调试 ===")
    
    # 创建LandlordAgent实例
    agent = LandlordAgent(api_key=os.getenv("QWEN_API_KEY") or "")
    
    # 测试场景1：第一轮首发出牌
    print("\n\n1. 测试场景1：第一轮首发出牌")
    print("=" * 50)
    
    # 设置游戏状态
    hand = ["3", "4", "5", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "2"]
    round_num = 1
    prev_card = "heart K"  # 这是其他玩家出的牌
    role = "农民"
    
    agent.set_hand(hand=hand, round=round_num, prev_card=prev_card, role=role)
    
    # 手动构建游戏状态（复制landlord_agent.py中的逻辑）
    # 获取历史数据
    history_records_json = agent.db.get_all()
    
    # 将JSON字符串转换为Python列表
    history_records = json.loads(history_records_json) if history_records_json else []
    
    # 将历史数据转换为结构化格式
    history_plays = []
    if history_records:
        for record in history_records:
            # 从字典中提取信息
            player = record.get('player', '')
            round_num_record = record.get('round', 1)
            card = record.get('card', '')
            
            # 提取牌的点数（去掉花色）
            rank = card.split()[-1] if card and card != '无' else ''
            
            history_plays.append({
                "回合": int(round_num_record),
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
            "炸弹": "四张同点数可压制任何非炸弹牌型",
            "顺子相关": "2和王不能参与顺子"
        },
        "玩家与阵营": [
            {"座位": "A", "阵营": "地主"},
            {"座位": "B", "阵营": "农民"},
            {"座位": "C", "阵营": "农民"}
        ],
        "局面": {
            "我的座位": "A" if role == "地主" else "B",
            "我的阵营": role,
            "轮到谁": "A" if role == "地主" else "B",  # 确保轮到谁与我的座位一致
            "阶段": "出牌",
            "桌面待跟牌(last_play)": {
                "是否存在": True if prev_card and prev_card != '无' else False,
                "出牌者": "B" if role == "地主" else "A",
                "牌型": "单张" if prev_card and prev_card != '无' else "无",
                "牌": [prev_card.split()[-1]] if prev_card and prev_card != '无' else [],
                "关键强度点": prev_card.split()[-1] if prev_card and prev_card != '无' else "",
                "张数": 1 if prev_card and prev_card != '无' else 0,
                "当前状态": "必须首发出牌，绝对不能选择Pass" if not (prev_card and prev_card != '无') else "必须跟牌，手牌中有比上一手更大的牌时绝对不能Pass",
                "提示信息": "根据规则，当你有能压制上一手牌的牌时，必须出牌压制，不能选择Pass。请严格遵循牌面大小规则：大王>小王>2>A>K>Q>J>10>9>8>7>6>5>4>3"
            },
            "历史出牌": history_plays,
            "我的手牌": {
                "表示格式": "仅点数不含花色",
                "牌": hand,
                "张数": len(hand)
            },
            "对手剩余张数": {
                "B": 15,  # 假设值，实际应用中需要跟踪
                "C": 15   # 假设值，实际应用中需要跟踪
            } if role == "地主" else {
                "A": 12,  # 假设值，实际应用中需要跟踪
                "C": 15   # 假设值，实际应用中需要跟踪
            },
            "不完全信息推断设置": {
                "策略": "保守（偏最坏情况/近似minimax）",
                "默认高风险牌假设可能存在": ["大王", "小王", "2", "炸弹"]
            }
        },
        "任务": {
            "目标": "最大化地主胜率" if role == "地主" else "最大化农民阵营胜率（允许为队友铺路/牺牲局部收益）"
        }
    }
    
    print("\n发送给AI的游戏状态：")
    print(json.dumps(game_state, ensure_ascii=False, indent=2))
    
    print("\n\n手牌：", hand)
    print("上一手牌：", prev_card)
    print("上一手牌点数：", prev_card.split()[-1] if prev_card else "无")
    # 正确的牌面大小顺序
    CARD_RANK = {"3":1, "4":2, "5":3, "6":4, "7":5, "8":6, "9":7, "10":8, "J":9, "Q":10, "K":11, "A":12, "2":13, "小王":14, "大王":15}
    prev_rank = prev_card.split()[-1] if prev_card else "无"
    has_better = any(CARD_RANK.get(card, 0) > CARD_RANK.get(prev_rank, 0) for card in hand) if prev_card else True
    print("是否有能压制的牌：", has_better if prev_card else "是（首发出牌）")
    
    # 测试场景2：第二轮跟牌
    print("\n\n2. 测试场景2：第二轮跟牌")
    print("=" * 50)
    
    hand2 = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "2", "2"]
    round_num2 = 2
    prev_card2 = "spade A"  # 这是其他玩家出的牌
    role2 = "农民"
    
    print("手牌：", hand2)
    print("上一手牌：", prev_card2)
    print("上一手牌点数：", prev_card2.split()[-1] if prev_card2 else "无")
    # 正确的牌面大小顺序
    CARD_RANK = {"3":1, "4":2, "5":3, "6":4, "7":5, "8":6, "9":7, "10":8, "J":9, "Q":10, "K":11, "A":12, "2":13, "小王":14, "大王":15}
    prev_rank2 = prev_card2.split()[-1] if prev_card2 else "无"
    has_better2 = any(CARD_RANK.get(card, 0) > CARD_RANK.get(prev_rank2, 0) for card in hand2) if prev_card2 else True
    better_cards2 = [card for card in hand2 if CARD_RANK.get(card, 0) > CARD_RANK.get(prev_rank2, 0)] if prev_card2 else hand2
    print("是否有能压制的牌：", has_better2 if prev_card2 else "是（首发出牌）")
    print("能压制的牌：", better_cards2 if prev_card2 else "所有手牌")

if __name__ == "__main__":
    debug_game_state()
