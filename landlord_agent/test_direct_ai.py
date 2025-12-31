  #!/usr/bin/env python3
"""
直接测试AI决策逻辑的脚本
"""

import json
import os
from landlord_agent import LandlordAgent

def test_direct_ai():
    """直接测试AI决策"""
    print("=== 直接测试AI决策 ===")
    
    # 创建LandlordAgent实例
    agent = LandlordAgent(api_key=os.getenv("QWEN_API_KEY") or "")
    
    # 清除数据库，避免历史数据影响测试
    agent.db.clear()
    
    # 直接设置测试场景2的状态
    hand = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "2", "2"]
    round_num = 2
    prev_card = "spade A"  # 上一手牌是黑桃A
    role = "农民"
    
    print(f"\n测试场景：跟牌A")
    print(f"手牌：{hand}")
    print(f"上一手牌：{prev_card}")
    print(f"角色：{role}")
    print(f"预期结果：必须出2压制A，不能Pass")
    
    # 设置游戏状态
    agent.set_hand(hand=hand, round=round_num, prev_card=prev_card, role=role)
    
    # 获取AI决策
    ai_decision = agent.decide()
    
    print(f"\nAI决策：")
    print(json.dumps(ai_decision, ensure_ascii=False, indent=2))
    
    if isinstance(ai_decision, dict):
        action = ai_decision.get('recommended_move', {}).get('action', 'unknown')
        cards = ai_decision.get('recommended_move', {}).get('cards', [])
        if action == 'play' and '2' in cards:
            print("\n✅ 测试通过：AI正确出2压制A")
        else:
            print(f"\n❌ 测试失败：AI选择{action}，但应该出2")
    
    # 测试场景3：首发出牌（无待跟牌）
    print("\n\n=== 测试场景3：首发出牌 ===")
    hand3 = ["3", "4", "5", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "2"]
    round_num3 = 1
    prev_card3 = None  # 无待跟牌
    role3 = "农民"
    
    agent.db.clear()  # 清除数据库
    
    print(f"手牌：{hand3}")
    print(f"上一手牌：无")
    print(f"角色：{role3}")
    print(f"预期结果：必须出牌，不能Pass")
    
    # 设置游戏状态
    agent.set_hand(hand=hand3, round=round_num3, prev_card=prev_card3, role=role3)
    
    # 获取AI决策
    ai_decision3 = agent.decide()
    
    print(f"\nAI决策：")
    print(json.dumps(ai_decision3, ensure_ascii=False, indent=2))
    
    if isinstance(ai_decision3, dict):
        action = ai_decision3.get('recommended_move', {}).get('action', 'unknown')
        if action == 'play':
            print("\n✅ 测试通过：AI正确选择出牌")
        else:
            print(f"\n❌ 测试失败：AI选择{action}，但应该出牌")

if __name__ == "__main__":
    test_direct_ai()