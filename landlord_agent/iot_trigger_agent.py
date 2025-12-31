"""
物联网触发式AI Agent系统
当巴法云平台有新数据时，自动调用DeepSeek生成出牌决策
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bemfa_client import BemfaClient
from landlord_agent import LandlordAgent
import time

BEMFA_UID = os.getenv("BEMFA_UID") or ""
BEMFA_TOPIC = os.getenv("BEMFA_TOPIC") or "2"
BEMFA_TYPE = int(os.getenv("BEMFA_TYPE") or "1")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("QWEN_API_KEY") or ""

class IoTTriggerAgent:
    def __init__(self):
        self.bemfa_client = BemfaClient(uid=BEMFA_UID)
        self.last_message = None
        self.running = True
        self.call_count = 0
    
    def process_message(self, message: str):
        """处理新消息并调用大模型"""
        if not message:
            return
        
        self.call_count += 1
        print(f"\n{'='*50}")
        print(f"🔔 第 {self.call_count} 次触发")
        print(f"📥 获取到新手牌数据: {message}")
        
        try:
            agent = LandlordAgent(api_key=DEEPSEEK_API_KEY)
            
            hand = message.split(',')
            hand = [card.strip() for card in hand if card.strip()]
            
            print(f"🃏 解析手牌: {hand}")
            
            agent.set_hand(
                hand=hand,
                round=1,
                prev_card=None,
                role="农民"
            )
            
            print("🤖 正在调用Qwen AI...")
            decision = agent.decide()
            
            print(f"✅ AI决策结果: {decision}")
            print(f"{'='*50}\n")
            
            return decision
            
        except Exception as e:
            print(f"❌ 处理出错: {e}")
            return None
    
    def monitor(self, interval: float = 3.0):
        """监控巴法云平台数据变化"""
        print("🚀 物联网触发式AI Agent系统启动")
        print(f"📡 监控巴法云平台 - Topic: {BEMFA_TOPIC}")
        print(f"⏱️ 轮询间隔: {interval}秒")
        print("🛑 按 Ctrl+C 停止监控\n")
        print("等待数据中...")
        
        try:
            while self.running:
                current_message = self.bemfa_client.get_latest_msg(
                    topic=BEMFA_TOPIC, 
                    type=BEMFA_TYPE
                )
                
                if current_message and current_message != self.last_message:
                    self.process_message(current_message)
                    self.last_message = current_message
                else:
                    if current_message:
                        print(f"⏳ {time.strftime('%H:%M:%S')} - 数据无变化")
                    else:
                        print(f"⏳ {time.strftime('%H:%M:%S')} - 等待数据...")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 监控已停止")
            self.running = False
    
    def single_trigger(self):
        """单次触发测试"""
        message = self.bemfa_client.get_latest_msg(
            topic=BEMFA_TOPIC, 
            type=BEMFA_TYPE
        )
        if message:
            return self.process_message(message)
        else:
            print("❌ 未获取到任何消息")
            return None


if __name__ == "__main__":
    agent = IoTTriggerAgent()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        interval = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
        agent.monitor(interval)
    else:
        print("🔄 单次触发测试")
        print("-" * 30)
        agent.single_trigger()
