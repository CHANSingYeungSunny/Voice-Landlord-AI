#!/usr/bin/env python3
"""
生成多轮次测试数据脚本
用于验证轮次解析和数据库插入功能
"""

import sys
import os
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 添加voice目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'voice'))

# 导入所需模块
from server import VoiceCardParser
from database import CardDB

def main():
    # 创建数据库实例
    db = CardDB()
    
    # 清空现有数据
    db.clear()
    
    # 创建解析器实例
    parser = VoiceCardParser()
    
    # 生成多轮次测试数据
    test_cases = [
        # 第一轮测试数据
        "玩家A在第一轮出了一张红桃3",
        "玩家B在第一轮出了一张红桃5",
        "玩家C在第一轮出了一张红桃7",
        
        # 第二轮测试数据
        "玩家A在第二轮出了一张黑桃10",
        "玩家B在第二轮出了一张黑桃Q",
        "玩家C在第二轮出了一张黑桃K",
        
        # 第三轮测试数据
        "玩家A在第三轮出了一张梅花A",
        "玩家B在第三轮出了一张梅花2",
        "玩家C在第三轮出了一张小王",
        
        # 第四轮测试数据
        "玩家A在第四轮出了一张方片J",
        "玩家B在第四轮出了一张方片Q",
        "玩家C在第四轮出了一张方片K",
        
        # 第五轮测试数据
        "玩家A在第五轮出了一张红桃A",
        "玩家B在第五轮出了一张红桃2",
        "玩家C在第五轮出了一张大王",
    ]
    
    print("=== 生成多轮次测试数据 ===")
    
    # 处理每个测试用例
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{test_case}")
        
        # 解析语音输入
        parsed_data = parser.parse(test_case)
        
        print(f"解析结果: {json.dumps(parsed_data, ensure_ascii=False, indent=2)}")
        
        # 如果解析成功，保存到数据库
        if parsed_data.get('player') and parsed_data.get('round') and parsed_data.get('card'):
            db.add(
                player=parsed_data['player'],
                round=parsed_data['round'],
                card=parsed_data['card'],
                weighting=parsed_data['weighting']
            )
            print("✓ 已保存到数据库")
        else:
            print("✗ 解析失败")
    
    print("\n=== 测试数据生成完成 ===")
    print("总测试用例数:", len(test_cases))
    
    # 检查数据库中的数据分布
    print("\n=== 数据库记录分布 ===")
    
    for round_num in range(1, 6):
        round_data = json.loads(db.get_round(round_num))
        print(f"第 {round_num} 轮: {len(round_data)} 条记录")

if __name__ == "__main__":
    main()
