"""
VoiceAI - 智能语音识别服务 (Python版本)
"""
import json
import os
import re
import sys
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# 添加landlord_agent目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'landlord_agent'))

# 导入landlord_agent模块
try:
    from landlord_agent import LandlordAgent
except ImportError as e:
    print(f"警告：无法导入landlord_agent模块: {e}")
    LandlordAgent = None

# Qwen API密钥
QWEN_API_KEY = os.getenv("QWEN_API_KEY") or ""


class VoiceCardParser:
    """扑克牌语音解析器"""
    
    PLAYER_MAP = {
        '玩家a': 'A', '玩家b': 'B', '玩家c': 'C',
        '玩家甲': 'A', '玩家乙': 'B', '玩家丙': 'C',
        'player a': 'A', 'player b': 'B', 'player c': 'C',
        'playera': 'A', 'playerb': 'B', 'playerc': 'C',
        'a': 'A', 'b': 'B', 'c': 'C',
    }
    
    SUIT_MAP = {
        '红桃': 'heart', '红心': 'heart', '红': 'heart',
        '黑桃': 'spade', '黑': 'spade',
        '梅花': 'club', '梅': 'club',
        '方片': 'diamond', '方': 'diamond', '片': 'diamond',
        '♦': 'diamond', '♠': 'spade', '♣': 'club', '♥': 'heart',
    }
    
    RANK_MAP = {
        'ace': 'A', '爱斯': 'A',
        '10': '10', '十': '10',
        'jack': 'J', '勾': 'J', '丁': 'J',
        'queen': 'Q', '圈': 'Q',
        'king': 'K', '开': 'K', '老k': 'K',
        'a': 'A',
        '2': '2', '二': '2', '两点': '2',
        '3': '3', '三': '3',
        '4': '4', '四': '4',
        '5': '5', '五': '5',
        '6': '6', '六': '6',
        '7': '7', '七': '7',
        '8': '8', '八': '8',
        '9': '9', '九': '9',
        'j': 'J',
        'q': 'Q',
        'k': 'K',
    }
    
    ROUND_MAP = {
        '第一轮': 1, '第一局': 1, '第一把': 1, '一': 1,
        '第二轮': 2, '第二局': 2, '第二把': 2, '二': 2,
        '第三轮': 3, '第三局': 3, '第三把': 3, '三': 3,
        '第四轮': 4, '第四局': 4, '第四把': 4, '四': 4,
        '第五轮': 5, '第五局': 5, '第五把': 5, '五': 5,
        '第六轮': 6, '第六局': 6, '第六把': 6, '六': 6,
        '第七轮': 7, '第七局': 7, '第七把': 7, '七': 7,
        '第八轮': 8, '第八局': 8, '第八把': 8, '八': 8,
        '第九轮': 9, '第九局': 9, '第九把': 9, '九': 9,
        '第十轮': 10, '第十局': 10, '第十把': 10, '十': 10,
    }
    
    def parse_player(self, text: str):
        text_lower = text.lower()
        for pattern, player in self.PLAYER_MAP.items():
            if pattern in text_lower:
                return player
        return None
    
    def parse_round(self, text: str):
        text_lower = text.lower()
        round_match = re.search(r'(?:第|)([一二三四五六七八九十\d]+)(?:轮|局|把)', text)
        if round_match:
            chinese_num = round_match.group(1)
            num_map = {
                '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
            }
            if chinese_num in num_map:
                return num_map[chinese_num]
            try:
                return int(chinese_num)
            except:
                pass
        
        for pattern, round_num in sorted(self.ROUND_MAP.items(), key=lambda x: -len(x[0])):
            if pattern in text_lower:
                return round_num
        return None
    
    def parse_suit(self, text: str):
        text_lower = text.lower()
        for pattern, suit in self.SUIT_MAP.items():
            if pattern.lower() in text_lower:
                return suit
        return None
    
    RANK_WEIGHT_MAP = {
        '2': 0.95,
        'A': 0.90,
        'K': 0.80,
        'Q': 0.70,
        'J': 0.60,
        '10': 0.50,
        '9': 0.45,
        '8': 0.40,
        '7': 0.35,
        '6': 0.30,
        '5': 0.25,
        '4': 0.20,
        '3': 0.15,
    }
    
    SPECIAL_WEIGHT_MAP = {
        'big_joker': 1.0,
        'little_joker': 0.98,
    }
    
    def parse_rank(self, text: str):
        text_lower = text.lower()
        sorted_patterns = sorted(self.RANK_MAP.items(), key=lambda x: -len(x[0]))
        for pattern, rank in sorted_patterns:
            if pattern in text_lower:
                return rank
        return None
    
    def calculate_weight(self, card: str, suit: str = None) -> float:
        if not card:
            return 0.5
        
        parts = card.split()
        if len(parts) >= 2:
            rank = parts[-1]
            if rank in self.RANK_WEIGHT_MAP:
                return self.RANK_WEIGHT_MAP[rank]
            if rank in self.RANK_MAP:
                mapped_rank = self.RANK_MAP[rank]
                return self.RANK_WEIGHT_MAP.get(mapped_rank, 0.5)
        
        if card in self.SPECIAL_WEIGHT_MAP:
            return self.SPECIAL_WEIGHT_MAP[card]
        
        return 0.5
    
    def parse(self, voice_text: str):
        text_lower = voice_text.lower()
        
        suit = self.parse_suit(voice_text)
        
        card_text = voice_text
        if suit:
            suit_chinese = None
            for pattern, s in self.SUIT_MAP.items():
                if s == suit and pattern.lower() in text_lower:
                    suit_chinese = pattern
                    break
            
            suit_match = re.search(rf'[{suit_chinese}](\w+)', voice_text) if suit_chinese else None
            if suit_match:
                card_text = suit_match.group(0)
            else:
                for pattern in ['红桃', '黑桃', '梅花', '方片']:
                    if pattern in voice_text:
                        idx = voice_text.find(pattern)
                        card_text = voice_text[idx:idx+10]
                        break
        
        rank = self.parse_rank(card_text)
        player = self.parse_player(voice_text)
        round_num = self.parse_round(voice_text)
        
        card = f"{suit} {rank}" if suit and rank else None
        
        if player and round_num and card:
            weighting = self.calculate_weight(card, suit)
            return {
                "player": player,
                "round": round_num,
                "card": card,
                "weighting": weighting,
                "original_text": voice_text,
                "timestamp": datetime.now().isoformat()
            }
        return {
            "player": None,
            "round": None,
            "card": None,
            "weighting": None,
            "original_text": voice_text,
            "error": "无法解析语音内容，请检查是否包含：玩家、轮次、花色、牌面",
            "timestamp": datetime.now().isoformat()
        }


class VoiceAIHandler(SimpleHTTPRequestHandler):
    
    API_CACHE = {}
    parser = VoiceCardParser()
    
    # 初始化landlord agent
    if LandlordAgent:
        try:
            landlord_agent = LandlordAgent(api_key=QWEN_API_KEY)
        except Exception as e:
            print(f"警告：无法初始化LandlordAgent: {e}")
            landlord_agent = None
    else:
        landlord_agent = None
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
    
    def send_json_response(self, data, status=200):
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', len(response.encode('utf-8')))
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == '/':
            self.path = '/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        
        elif path == '/api/health':
            self.send_json_response({
                'status': 'ok',
                'service': 'VoiceAI Recognition',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            })
        
        elif path == '/api/history':
            history = []
            for key, value in self.API_CACHE.items():
                history.append({
                    'id': key,
                    'original_text': value.get('original_text', '')[:100],
                    'timestamp': value.get('timestamp'),
                    'player': value.get('player'),
                    'round': value.get('round'),
                    'card': value.get('card')
                })
            self.send_json_response({
                'count': len(history),
                'results': history[:20][::-1]
            })
        
        elif path.startswith('/api/result/'):
            result_id = path.split('/api/result/')[1]
            for key, value in self.API_CACHE.items():
                if result_id in key:
                    self.send_json_response(value)
                    return
            self.send_json_response({'error': '结果未找到'}, 404)
        
        else:
            return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        path = urlparse(self.path).path
        
        if path == '/api/recognize':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                audio_text = data.get('audio_text', '')
                timestamp = data.get('timestamp', datetime.now().isoformat())
                
                if not audio_text:
                    self.send_json_response({
                        'error': '缺少音频文本内容',
                        'message': '请提供 audio_text 字段'
                    }, 400)
                    return
                
                cache_key = f"{audio_text[:50]}-{timestamp}"
                if cache_key in self.API_CACHE:
                    print(f"返回缓存结果")
                    self.send_json_response(self.API_CACHE[cache_key])
                    return
                
                print(f"解析语音输入: {audio_text}")
                result = self.parser.parse(audio_text)
                self.API_CACHE[cache_key] = result
                
                if len(self.API_CACHE) > 100:
                    first_key = next(iter(self.API_CACHE))
                    del self.API_CACHE[first_key]
                
                self.send_json_response(result)
                
            except json.JSONDecodeError:
                self.send_json_response({'error': '无效的JSON格式'}, 400)
            except Exception as e:
                print(f"Error: {e}")
                self.send_json_response({'error': '服务器错误', 'message': str(e)}, 500)
        
        elif path == '/api/process_voice_command':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                audio_text = data.get('audio_text', '')
                timestamp = data.get('timestamp', datetime.now().isoformat())
                
                if not audio_text:
                    self.send_json_response({
                        'error': '缺少音频文本内容',
                        'message': '请提供 audio_text 字段'
                    }, 400)
                    return
                
                cache_key = f"command-{audio_text[:50]}-{timestamp}"
                if cache_key in self.API_CACHE:
                    print(f"返回缓存结果")
                    self.send_json_response(self.API_CACHE[cache_key])
                    return
                
                print(f"处理语音命令: {audio_text}")
                
                # 解析语音输入
                parsed_data = self.parser.parse(audio_text)
                
                # 构建处理结果
                process_result = {
                    'timestamp': timestamp,
                    'voice_text': audio_text,
                    'parsed_data': parsed_data,
                    'ai_decision': None,
                    'status': 'parse_success' if parsed_data.get('player') and parsed_data.get('round') and parsed_data.get('card') else 'parse_error'
                }
                
                # 如果解析成功，记录到数据库并获取AI决策
                if process_result['status'] == 'parse_success' and self.landlord_agent:
                    try:
                        # 记录到数据库
                        self.landlord_agent.record(
                            player=parsed_data['player'],
                            round=parsed_data['round'],
                            card=parsed_data['card'],
                            weighting=parsed_data['weighting']
                        )
                        
                        # 获取AI决策
                        # 设置当前游戏状态（示例）
                        current_hand = self._get_current_hand(parsed_data['round'])
                        prev_card = parsed_data['card']  # 假设上一手是当前解析的牌
                        role = "农民"  # 默认角色
                        
                        self.landlord_agent.set_hand(
                            hand=current_hand,
                            round=parsed_data['round'],
                            prev_card=prev_card,
                            role=role
                        )
                        
                        # 获取AI决策
                        ai_decision = self.landlord_agent.decide()
                        process_result['ai_decision'] = ai_decision
                        process_result['status'] = 'success'
                        
                    except Exception as e:
                        print(f"AI决策错误: {e}")
                        process_result['status'] = 'ai_error'
                        process_result['error'] = f'AI决策生成失败: {str(e)}'
                elif not self.landlord_agent:
                    process_result['status'] = 'no_agent'
                    process_result['error'] = 'landlord_agent模块未初始化'
                
                # 缓存结果
                self.API_CACHE[cache_key] = process_result
                
                if len(self.API_CACHE) > 100:
                    first_key = next(iter(self.API_CACHE))
                    del self.API_CACHE[first_key]
                
                self.send_json_response(process_result)
                
            except json.JSONDecodeError:
                self.send_json_response({'error': '无效的JSON格式'}, 400)
            except Exception as e:
                print(f"Error: {e}")
                self.send_json_response({'error': '服务器错误', 'message': str(e)}, 500)
        
        else:
            self.send_json_response({'error': '接口不存在'}, 404)
    
    def _get_current_hand(self, round_num: int) -> list:
        """获取当前手牌（示例实现）"""
        # 实际应用中，应该从数据库或其他来源获取当前手牌
        # 这里提供一个示例实现
        return ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]


def run_server(port=3000):
    """启动服务器"""
    server = HTTPServer(('0.0.0.0', port), VoiceAIHandler)
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🎤 VoiceAI 智能扑克牌识别服务                           ║
║                                                          ║
║   Server running on: http://localhost:{port}               ║
║                                                          ║
║   API Endpoints:                                         ║
║   • POST /api/recognize            - 扑克牌识别接口       ║
║   • POST /api/process_voice_command - 处理语音命令并获取AI决策 ║
║   • GET  /api/health               - 健康检查             ║
║   • GET  /api/result/:id           - 获取特定结果         ║
║   • GET  /api/history              - 获取历史记录         ║
║                                                          ║
║   支持格式: 玩家A在第一轮出了一张红桃K                    ║
║                                                          ║
║   按 Ctrl+C 停止服务器                                   ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        server.server_close()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    run_server(port)
