#!/usr/bin/env python3
"""
数据库查看测试文件
功能：连接到cards.db数据库，查询并显示记录
"""

import json
import sys
import os

# 添加landlord_agent目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'landlord_agent'))

from database import CardDB

def main():
    print("=== 数据库记录查询工具 ===")
    
    # 数据库路径配置 - 只连接landlord_agent目录下的数据库
    LANDLORD_DB_PATH = "./landlord_agent/cards.db"
    LANDLORD_DB_NAME = "landlord_agent目录数据库"
    
    # 创建数据库实例
    try:
        selected_db = CardDB(LANDLORD_DB_PATH)
        print(f"✓ 成功连接到 {LANDLORD_DB_NAME}")
    except Exception as e:
        print(f"✗ 连接 {LANDLORD_DB_NAME} 失败: {e}")
        return
    
    while True:
        print("\n操作选项:")
        print("1. 查询所有记录")
        print("2. 按玩家查询记录")
        print("3. 按轮次查询记录")
        print("4. 退出程序")
        
        action = input("\n请选择操作 (1-4): ").strip()
        
        if action == "1":
            print(f"\n--- {LANDLORD_DB_NAME} - 所有记录 ---\n")
            try:
                records = selected_db.get_all()
                data = json.loads(records)
                if data:
                    for idx, record in enumerate(data, 1):
                        print(f"记录 {idx}:")
                        print(f"  玩家: {record['player']}")
                        print(f"  轮次: {record['round']}")
                        print(f"  牌型: {record['card']}")
                        print(f"  权重: {record['weighting']}")
                        print()
                    print(f"总计 {len(data)} 条记录")
                else:
                    print("数据库中没有记录")
            except Exception as e:
                print(f"查询失败: {e}")
        
        elif action == "2":
            player = input("请输入玩家标识 (如 A、B、C): ").strip().upper()
            print(f"\n--- {LANDLORD_DB_NAME} - 玩家 {player} 的所有记录 ---\n")
            try:
                records = selected_db.get_player(player)
                data = json.loads(records)
                if data:
                    for idx, record in enumerate(data, 1):
                        print(f"记录 {idx}:")
                        print(f"  轮次: {record['round']}")
                        print(f"  牌型: {record['card']}")
                        print(f"  权重: {record['weighting']}")
                        print()
                    print(f"总计 {len(data)} 条记录")
                else:
                    print(f"玩家 {player} 没有记录")
            except Exception as e:
                print(f"查询失败: {e}")
        
        elif action == "3":
            try:
                round_num = int(input("请输入轮次 (数字): ").strip())
                print(f"\n--- {LANDLORD_DB_NAME} - 第 {round_num} 轮的所有记录 ---\n")
                records = selected_db.get_round(round_num)
                data = json.loads(records)
                if data:
                    for idx, record in enumerate(data, 1):
                        print(f"记录 {idx}:")
                        print(f"  玩家: {record['player']}")
                        print(f"  牌型: {record['card']}")
                        print(f"  权重: {record['weighting']}")
                        print()
                    print(f"总计 {len(data)} 条记录")
                else:
                    print(f"第 {round_num} 轮没有记录")
            except ValueError:
                print("请输入有效的数字")
            except Exception as e:
                print(f"查询失败: {e}")
        
        elif action == "4":
            print("\n✓ 退出程序")
            break
        
        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()
