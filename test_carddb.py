#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接测试CardDB数据库操作
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'landlord_agent'))

from database import CardDB

def test_carddb_operations():
    print("=== 测试CardDB数据库操作 ===")
    
    # 数据库路径
    db_path = os.path.join(os.path.dirname(__file__), 'landlord_agent', 'cards.db')
    print(f"数据库路径: {db_path}")
    
    # 创建CardDB实例
    card_db = CardDB(db_path)
    print("✓ 创建CardDB实例成功")
    
    # 清除现有数据
    card_db.clear()
    print("✓ 清除数据库成功")
    
    # 测试添加单条记录
    card_db.add(player="A", round=1, card="heart K", weighting=0.8)
    print("✓ 添加单条记录成功")
    
    # 测试批量添加记录
    records = [
        {"player": "B", "round": 2, "card": "spade A", "weighting": 0.9},
        {"player": "C", "round": 3, "card": "diamond 2", "weighting": 1.0}
    ]
    card_db.add_batch(records)
    print("✓ 批量添加记录成功")
    
    # 测试查询所有记录
    all_records_json = card_db.get_all()
    all_records = json.loads(all_records_json)
    print(f"✓ 查询所有记录成功，共 {len(all_records)} 条")
    for i, record in enumerate(all_records, 1):
        print(f"  记录 {i}: {record}")
    
    # 测试按玩家查询
    player_records_json = card_db.get_player("A")
    player_records = json.loads(player_records_json)
    print(f"✓ 查询玩家A的记录成功，共 {len(player_records)} 条")
    for record in player_records:
        print(f"  {record}")
    
    # 测试按轮次查询
    round_records_json = card_db.get_round(2)
    round_records = json.loads(round_records_json)
    print(f"✓ 查询第2轮的记录成功，共 {len(round_records)} 条")
    for record in round_records:
        print(f"  {record}")
    
    print("\n=== 所有CardDB测试完成 ===")

if __name__ == "__main__":
    test_carddb_operations()