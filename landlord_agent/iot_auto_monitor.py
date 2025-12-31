"""
物联网触发式AI Agent - 自动化监控脚本
功能：持续监控巴法云平台，当收到新数据时自动调用大模型生成出牌决策
使用方法：python iot_auto_monitor.py
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bemfa_client import BemfaClient
from landlord_agent import LandlordAgent

BEMFA_UID = os.getenv("BEMFA_UID") or ""
BEMFA_TOPIC = os.getenv("BEMFA_TOPIC") or "2"
BEMFA_TYPE = int(os.getenv("BEMFA_TYPE") or "1")
QWEN_API_KEY = os.getenv("QWEN_API_KEY") or ""

LOG_FILE = "iot_trigger_log.txt"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def parse_hand(hand_str):
    """解析手牌字符串"""
    if not hand_str:
        return []
    cards = hand_str.replace('，', ',').split(',')
    return [card.strip() for card in cards if card.strip()]

def call_ai_decision(hand_data):
    """调用AI生成决策"""
    try:
        log(f"🤖 开始调用Qwen AI...")
        log(f"🃏 手牌数据: {hand_data}")
        
        agent = LandlordAgent(api_key=QWEN_API_KEY)
        
        # 清空数据库，避免历史数据影响当前决策
        agent.db.clear()
        
        hand = parse_hand(hand_data)
        log(f"📋 解析后的手牌: {hand}")
        
        agent.set_hand(
            hand=hand,
            round=1,
            prev_card=None,
            role="农民"
        )
        
        decision = agent.decide()
        log(f"✅ AI决策结果: {decision}")
        
        return decision
        
    except Exception as e:
        log(f"❌ AI调用错误: {str(e)}")
        return None

def main():
    print("\n" + "="*60)
    print("🚀 物联网触发式AI Agent - 自动化监控系统")
    print("="*60)
    print(f"📡 巴法云配置:")
    print(f"   - UID: {'已配置' if BEMFA_UID else '未配置'}")
    print(f"   - Topic: {BEMFA_TOPIC}")
    print(f"   - Type: {BEMFA_TYPE}")
    print(f"🤖 Qwen API: {'已配置' if QWEN_API_KEY else '未配置'}")
    print("-"*60)
    print("🛑 按 Ctrl+C 停止监控")
    print("="*60 + "\n")
    
    bemfa_client = BemfaClient(uid=BEMFA_UID)
    last_data = None
    trigger_count = 0
    
    log("="*50)
    log("🚀 监控系统启动")
    log(f"📡 监控Topic: {BEMFA_TOPIC}")
    log("="*50)
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            try:
                current_data = bemfa_client.get_latest_msg(
                    topic=BEMFA_TOPIC, 
                    type=BEMFA_TYPE
                )
                
                if current_data is None:
                    log(f"[{current_time}] ⚠️ 无法获取数据，连接可能异常")
                elif current_data != last_data:
                    trigger_count += 1
                    log("="*50)
                    log(f"🔔 触发 #{trigger_count}")
                    log(f"📥 新数据: {current_data}")
                    
                    decision = call_ai_decision(current_data)
                    
                    if decision:
                        log(f"🎯 决策已生成: {decision}")
                    else:
                        log("⚠️ 决策生成失败")
                    
                    last_data = current_data
                    log("="*50)
                else:
                    print(f"[{current_time}] ⏳ 数据无变化 (等待中...)", end="\r")
                    
            except Exception as e:
                log(f"[{current_time}] ❌ 错误: {str(e)}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        log("\n" + "="*50)
        log("👋 监控已停止")
        log(f"📊 总触发次数: {trigger_count}")
        log("="*50)
        print("\n监控已停止")


if __name__ == "__main__":
    main()
