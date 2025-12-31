"""
巴法云物联网平台客户端
用于获取设备数据（手牌信息）
"""

import urllib.request
import urllib.parse
import json
from typing import Optional, Dict, Any, List

BEMFA_API_BASE = "https://apis.bemfa.com/va"

class BemfaClient:
    def __init__(self, uid: str):
        self.uid = uid
    
    def _get(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """发送GET请求"""
        query_string = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_string}"
        
        try:
            with urllib.request.urlopen(full_url, timeout=10) as response:
                data = response.read().decode('utf-8')
                return json.loads(data)
        except Exception as e:
            print(f"请求错误: {e}")
            return None
    
    def get_msg(self, topic: str, type: int = 1) -> Optional[List[Dict[str, Any]]]:
        """
        获取主题消息
        
        参数:
            topic: 主题名称
            type: 消息类型（默认1）
        
        返回:
            消息列表，如果失败返回None
        """
        url = f"{BEMFA_API_BASE}/getmsg"
        params = {
            "uid": self.uid,
            "topic": topic,
            "type": type
        }
        
        result = self._get(url, params)
        
        if result and result.get("code") == 0:
            return result.get("data", [])
        elif result:
            print(f"获取消息失败: {result.get('message')}")
        return None
    
    def get_latest_msg(self, topic: str, type: int = 1) -> Optional[str]:
        """
        获取主题最新一条消息的内容
        """
        data = self.get_msg(topic, type)
        if data and len(data) > 0:
            return data[0].get("msg")
        return None


if __name__ == "__main__":
    import os
    uid = os.getenv("BEMFA_UID") or ""
    if not uid:
        print("请设置BEMFA_UID环境变量")
    else:
        client = BemfaClient(uid=uid)
        
        print("=== 巴法云测试 ===")
        msg = client.get_latest_msg(topic="2", type=1)
        print(f"最新消息: {msg}")
