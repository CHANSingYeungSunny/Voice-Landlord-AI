#!/usr/bin/env python3
"""
Voice-Landlord Agent Integration Module
功能：连接语音识别系统与地主AI决策系统
"""

import sys
import os
import json
from datetime import datetime

# 添加landlord_agent目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 添加voice目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'voice'))

# 导入所需模块
try:
    # 直接从voice目录导入
    from server import VoiceCardParser
    from landlord_agent import LandlordAgent
except ImportError as e:
    print(f"导入错误: {e}")
    print("当前Python路径:", sys.path)
    sys.exit(1)

# Qwen API密钥
QWEN_API_KEY = os.getenv("QWEN_API_KEY") or ""

class VoiceLandlordIntegrator:
    """语音地主AI整合器"""
    
    def __init__(self, api_key=QWEN_API_KEY):
        """初始化整合器"""
        self.parser = VoiceCardParser()
        # 显式指定数据库路径为当前目录下的cards.db
        import os
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cards.db')
        self.agent = LandlordAgent(api_key=api_key, db_path=db_path)
        self.history = []
    
    def parse_voice_input(self, voice_text: str) -> dict:
        """解析语音输入并转换为结构化数据"""
        return self.parser.parse(voice_text)
    
    def process_voice_command(self, voice_text: str) -> dict:
        """处理语音命令并返回AI决策"""
        # 解析语音输入
        parsed_data = self.parser.parse(voice_text)
        
        # 记录处理历史
        process_record = {
            'timestamp': datetime.now().isoformat(),
            'voice_text': voice_text,
            'parsed_data': parsed_data,
            'ai_decision': None
        }
        
        # 如果解析成功，记录到数据库并获取AI决策
        if parsed_data.get('player') and parsed_data.get('round') and parsed_data.get('card'):
            # 记录到数据库
            self.agent.record(
                player=parsed_data['player'],
                round=parsed_data['round'],
                card=parsed_data['card'],
                weighting=parsed_data['weighting']
            )
            
            # 获取AI决策
            try:
                # 设置当前游戏状态
                # 注意：这里需要根据实际情况调整，可能需要从数据库获取更多信息
                current_hand = self._get_current_hand(parsed_data['round'])
                prev_card = parsed_data['card']  # 假设上一手是当前解析的牌
                role = "农民"  # 默认角色，可以根据实际情况调整
                
                self.agent.set_hand(
                    hand=current_hand,
                    round=parsed_data['round'],
                    prev_card=prev_card,
                    role=role
                )
                
                # 获取AI决策
                ai_decision = self.agent.decide()
                process_record['ai_decision'] = ai_decision
                
                return {
                    'status': 'success',
                    'parsed_data': parsed_data,
                    'ai_decision': ai_decision
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'parsed_data': parsed_data,
                    'error': f'AI决策生成失败: {str(e)}'
                }
        else:
            return {
                'status': 'parse_error',
                'parsed_data': parsed_data,
                'error': parsed_data.get('error', '语音解析失败')
            }
    
    def _get_current_hand(self, round_num: int) -> list:
        """获取当前手牌（示例实现）"""
        # 根据不同轮次提供不同的测试手牌，验证不同场景
        if round_num == 1:
            # 第一轮手牌：包含各种大小的牌，测试首发出牌
            return ["3", "4", "5", "7", "8", "9", "10", "J", "Q", "K", "A", "2", "2"]
        elif round_num == 2:
            # 第二轮手牌：包含能压制黑桃A的牌（2）
            return ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "2", "2"]
        else:
            # 其他轮次默认手牌
            return ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
    
    def get_history(self) -> list:
        """获取处理历史"""
        return self.history
    
    def clear_history(self):
        """清空处理历史"""
        self.history.clear()

def main():
    """测试整合功能"""
    print("=== Voice-Landlord AI 整合测试 ===")
    
    # 创建整合器实例
    integrator = VoiceLandlordIntegrator()
    
    # 测试场景1：第一轮首发出牌（无待跟牌）
    print("\n=====================================")
    print("测试场景1：第一轮首发出牌")
    print("=====================================")
    test_voice_text = "玩家A在第一轮出了一张红桃K"
    print(f"测试语音输入: {test_voice_text}")
    print("预期结果: AI必须出牌，不能Pass")
    
    # 处理语音命令
    result = integrator.process_voice_command(test_voice_text)
    
    # 打印结果
    print(f"\n处理结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试场景2：第二轮跟牌（有能压制的牌）
    print("\n\n===================================== ")
    print("测试场景2：第二轮跟牌（有能压制的牌）")
    print("===================================== ")
    test_voice_text2 = "玩家B在第二轮出了一张黑桃A"
    print(f"测试语音输入: {test_voice_text2}")
    print("预期结果: AI手牌中有2，必须出2压制A，不能Pass")
    
    # 手动清除数据库，避免历史数据影响测试
    integrator.agent.db.clear()
    
    # 处理语音命令
    result2 = integrator.process_voice_command(test_voice_text2)
    
    # 打印结果
    print(f"\n处理结果:")
    print(json.dumps(result2, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
