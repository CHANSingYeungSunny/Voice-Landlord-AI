#!/usr/bin/env python3
"""
清空数据库脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入数据库模块
from database import CardDB

def main():
    print("=== 清空数据库 ===")
    
    # 创建数据库实例
    db = CardDB()
    
    # 清空数据库
    db.clear()
    
    print("✓ 数据库已清空")

if __name__ == "__main__":
    main()
