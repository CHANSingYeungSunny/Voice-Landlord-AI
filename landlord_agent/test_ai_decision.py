#!/usr/bin/env python3
"""
Test AI Decision Logic
功能：测试AI在不同牌型下的决策是否正确
"""

import sys
import os
import json
from landlord_agent import LandlordAgent
from voice_landlord_integration_updated import VoiceLandlordIntegrator

def test_ai_leading():
    """测试AI首发出牌（必须出牌，不能pass）"""
    print("=== 测试1: AI首发出牌 ===")
    integrator = VoiceLandlordIntegrator()
    
    # 清空数据库
    integrator.agent.db.clear()
    
    # 测试语音输入 - 模拟AI首发出牌（无前置牌）
    print(f"测试：AI作为首家出牌")
    
    # 手动设置AI手牌和状态
    hand = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
    integrator.agent.set_hand(
        hand=hand,
        round=1,
        prev_card=None,  # 首发出牌，无上一手牌
        role="农民"
    )
    
    # 获取AI决策
    ai_decision = integrator.agent.decide()
    
    # 打印结果
    print(f"AI手牌：{hand}")
    print(f"AI决策：{json.dumps(ai_decision, ensure_ascii=False, indent=2)}")
    
    # 验证结果：首发出牌时必须出牌，不能pass
    action = ai_decision.get("recommended_move", {}).get("action", "")
    if action == "pass":
        print("❌ 错误：首发出牌时AI不应该选择pass！")
        return False
    else:
        print("✅ 正确：首发出牌时AI选择了出牌")
        return True

def test_ai_following():
    """测试AI跟牌决策"""
    print("\n=== 测试2: AI跟牌决策 ===")
    integrator = VoiceLandlordIntegrator()
    
    # 清空数据库
    integrator.agent.db.clear()
    
    # 设置上一手牌为红桃K
    prev_card = "heart K"
    
    # 测试语音输入 - 记录上一手牌
    test_voice_text = "玩家A在第一轮出了一张红桃K"
    print(f"测试：玩家A出了 {prev_card}")
    
    # 处理语音命令
    result = integrator.process_voice_command(test_voice_text)
    
    # 手动设置AI手牌和状态
    hand = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
    integrator.agent.set_hand(
        hand=hand,
        round=1,
        prev_card=prev_card,
        role="农民"
    )
    
    # 获取AI决策
    ai_decision = integrator.agent.decide()
    
    # 打印结果
    print(f"AI手牌：{hand}")
    print(f"上一手牌：{prev_card}")
    print(f"AI决策：{json.dumps(ai_decision, ensure_ascii=False, indent=2)}")
    
    # 验证结果：AI有A和2，可以打K，不应该pass
    action = ai_decision.get("recommended_move", {}).get("action", "")
    if action == "pass":
        print("❌ 错误：AI有A和2，可以打K，不应该选择pass！")
        return False
    else:
        print("✅ 正确：AI选择了打K")
        return True

def test_voice_parsing():
    """测试语音解析功能"""
    print("\n=== 测试3: 语音解析功能 ===")
    integrator = VoiceLandlordIntegrator()
    
    # 测试不同的语音输入
    test_cases = [
        "玩家A在第一轮出了一张红桃K",
        "玩家B在第二轮出了一张黑桃A",
        "玩家C在第三轮出了一张方片2"
    ]
    
    success_count = 0
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_text}")
        parsed_data = integrator.parser.parse(test_text)
        print(f"解析结果：{json.dumps(parsed_data, ensure_ascii=False, indent=2)}")
        
        # 验证解析结果
        if parsed_data.get("player") and parsed_data.get("round") and parsed_data.get("card"):
            print("✅ 解析成功")
            success_count += 1
        else:
            print("❌ 解析失败")
    
    print(f"\n解析成功率：{success_count}/{len(test_cases)}")
    return success_count == len(test_cases)

def main():
    """运行所有测试"""
    print("=== AI决策和语音解析综合测试 ===")
    
    test_results = []
    
    # 运行测试
    test_results.append(test_ai_leading())
    test_results.append(test_ai_following())
    test_results.append(test_voice_parsing())
    
    # 总结测试结果
    print("\n=== 测试总结 ===")
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        print("✅ 所有测试通过！landlord_agent和voice集成良好")
        return 0
    else:
        print(f"❌ {passed}/{total} 测试通过，存在集成问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
