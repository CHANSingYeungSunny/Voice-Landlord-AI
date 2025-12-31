#!/usr/bin/env python3
"""
测试AI在持有单张K且作为首发出牌时错误选择pass的问题
"""

import sys
import os
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from landlord_agent import LandlordAgent

# 创建测试用例
def test_ai_pass_issue():
    print("=== 测试AI错误pass问题 ===")
    
    # 创建AI代理
    agent = LandlordAgent(api_key=os.getenv("QWEN_API_KEY") or "")
    
    # 清空数据库，避免历史数据影响
    agent.db.clear()
    print("数据库已清空")
    
    # 测试用例1：持有K，作为首发出牌
    hand = ["K"]
    round_num = 1
    prev_card = None
    role = "农民"
    
    print(f"\n测试用例1：手牌={hand}, 轮数={round_num}, 上一手牌={prev_card}, 角色={role}")
    print(f"规则要求：作为首发出牌，必须出牌，不能pass")
    
    agent.set_hand(hand=hand, round=round_num, prev_card=prev_card, role=role)
    
    # 打印完整的game_state以便分析
    import json
    history_records_json = agent.db.get_all()
    history_records = json.loads(history_records_json) if history_records_json else []
    
    history_plays = []
    if history_records:
        for record in history_records:
            player = record.get('player', '')
            round_num = record.get('round', 1)
            card = record.get('card', '')
            rank = card.split()[-1] if card and card != '无' else ''
            history_plays.append({
                "回合": int(round_num),
                "玩家": player,
                "动作": "出牌" if card and card != '无' else "Pass",
                "牌型": "单张" if card and card != '无' else "Pass",
                "牌": [rank] if card and card != '无' else []
            })
    
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
            "我的座位": "A" if role == "地主" else "B",
            "我的阵营": role,
            "轮到谁": "A" if role == "地主" else "B",
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
                "B": 15,
                "C": 15
            } if role == "地主" else {
                "A": 12,
                "C": 15
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
    
    print(f"\n完整game_state: {json.dumps(game_state, ensure_ascii=False, indent=2)}")
    
    decision = agent.decide()
    
    print(f"AI决策结果: {decision}")
    
    # 解析决策
    if isinstance(decision, dict):
        action = decision.get("recommended_move", {}).get("action")
        cards = decision.get("recommended_move", {}).get("cards", [])
        
        print(f"\n决策详情：")
        print(f"  动作: {action}")
        print(f"  牌: {cards}")
        
        if action == "pass":
            print("❌ 错误：AI选择了pass，违反了首发出牌规则")
            return False
        elif action == "play" and cards == ["K"]:
            print("✅ 正确：AI选择了出K")
            return True
        else:
            print("⚠️ 其他错误：AI选择了出其他牌")
            return False
    else:
        print("❌ 错误：AI返回了非JSON格式的响应")
        return False

# 测试用例2：模拟iot_auto_monitor.py的调用方式
def test_iot_scenario():
    print("\n=== 测试IoT场景 ===")
    
    # 模拟iot_auto_monitor.py中的调用
    from bemfa_client import BemfaClient
    
    # 创建AI代理
    agent = LandlordAgent(api_key=os.getenv("QWEN_API_KEY") or "")
    
    # 模拟iot_auto_monitor.py中的parse_hand函数
    def parse_hand(hand_str):
        if not hand_str:
            return []
        cards = hand_str.replace('，', ',').split(',')
        return [card.strip() for card in cards if card.strip()]
    
    # 模拟iot_auto_monitor.py中的call_ai_decision函数
    def call_ai_decision(hand_data):
        print(f"\n调用AI决策，手牌数据: {hand_data}")
        
        hand = parse_hand(hand_data)
        print(f"解析后的手牌: {hand}")
        
        agent.set_hand(
            hand=hand,
            round=1,  # 硬编码轮数1
            prev_card=None,  # 硬编码上一手牌为None
            role="农民"
        )
        
        decision = agent.decide()
        print(f"AI决策结果: {decision}")
        
        return decision
    
    # 测试IoT场景
    hand_data = "K"
    decision = call_ai_decision(hand_data)
    
    # 解析决策
    if isinstance(decision, dict):
        action = decision.get("recommended_move", {}).get("action")
        cards = decision.get("recommended_move", {}).get("cards", [])
        
        print(f"\nIoT场景决策详情：")
        print(f"  动作: {action}")
        print(f"  牌: {cards}")
        
        if action == "pass":
            print("❌ 错误：IoT场景下AI选择了pass，违反了首发出牌规则")
            return False
        elif action == "play" and cards == ["K"]:
            print("✅ 正确：IoT场景下AI选择了出K")
            return True
        else:
            print("⚠️ 其他错误：IoT场景下AI选择了出其他牌")
            return False
    else:
        print("❌ 错误：IoT场景下AI返回了非JSON格式的响应")
        return False

if __name__ == "__main__":
    # 运行测试
    test1_result = test_ai_pass_issue()
    test2_result = test_iot_scenario()
    
    print("\n" + "="*50)
    print("测试总结：")
    print(f"测试用例1 (直接测试): {'通过' if test1_result else '失败'}")
    print(f"测试用例2 (IoT场景): {'通过' if test2_result else '失败'}")
    print("="*50)
