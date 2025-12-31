# Voice Landlord AI

## 🌐 Language / 语言选择

| [English](#english) | [中文](#中文) |
|---------------------|---------------|

---

## English

### Project Introduction

A compact integration of voice recognition and Landlord AI decision-making, enabling seamless workflow from voice input to optimal card-playing decisions via the Qwen-Turbo model, offering intelligent player assistance.

### Core Features

- Voice parsing from natural language to structured data
- AI-powered optimal card-playing decisions
- Dual-server support (Python/Node.js)
- HTTP APIs for voice command processing and AI decisions
- Historical record management
- Real-time feedback

### Quick Start

```bash
# Install dependencies
cd No_More_Ghosting
pip install -r requirements.txt
cd voice && npm install

# Run servers (choose one)
python server.py        # http://localhost:3000
node server.js         # http://localhost:3001

# Test integration
cd landlord_agent
python voice_landlord_integration_updated.py
```

### Key APIs

- `POST /api/process_voice_command` - Process voice commands and get AI decisions
- `POST /api/recognize` - Voice recognition
- `GET /api/history` - Query history
- `GET /api/health` - Health check

### Technology Stack

Python, Node.js, Express, Qwen-Turbo, SQLite, JSON

### Notes

- Set valid Qwen API key
- Voice commands: "Player X played Z card in round Y"
- AI decisions based on default hand (adjust for real games)

### License

MIT License

---

## 中文

### 项目简介

这是一个将语音识别系统与地主AI决策系统整合的项目，实现了从语音输入到AI决策的完整流程。通过自然语言语音指令，系统能够解析游戏状态，并基于Qwen-Turbo模型生成最优出牌决策，为玩家提供智能辅助。

### 核心功能

- **语音解析**: 将自然语言语音指令（如"玩家A在第一轮出了一张红桃K"）解析为结构化数据
- **AI决策**: 基于解析后的游戏状态，使用Qwen-Turbo模型生成最优出牌决策
- **双服务器架构**: 同时支持Python和Node.js两种服务器实现
- **API接口**: 提供HTTP API接口，支持语音命令处理和AI决策获取
- **历史记录**: 保存和查询历史语音解析结果和AI决策
- **实时反馈**: 支持实时处理语音命令并返回决策结果

### 目录结构

```
No_More_Ghosting/
├── landlord_agent/          # 地主AI决策系统
│   ├── landlord_agent.py    # 核心AI决策逻辑
│   ├── voice_landlord_integration_updated.py  # 语音-AI整合模块
│   └── ...
├── voice/                   # 语音识别系统
│   ├── server.py           # Python语音识别服务器
│   ├── server.js           # Node.js语音识别服务器
│   ├── package.json        # Node.js依赖配置
│   ├── index.html          # 前端页面
│   └── ...
├── card_db.py              # 卡片数据库管理
├── testfile.py             # 测试文件
└── README.md              # 项目文档
```

### 安装和运行

#### 1. 环境准备

确保已安装Python 3.8+和Node.js 16+，并安装必要的依赖：

```bash
# 进入项目目录
cd No_More_Ghosting

# 安装Python依赖（如果有requirements.txt文件）
pip install -r requirements.txt

# 进入voice目录，安装Node.js依赖
cd voice
npm install
```

#### 2. 运行Python语音识别服务器

```bash
# 进入voice目录
cd voice

# 启动Python服务器
python server.py
```
Python服务器默认运行在 http://localhost:3000

#### 3. 运行Node.js语音识别服务器

```bash
# 进入voice目录
cd voice

# 启动Node.js服务器
node server.js
```
Node.js服务器默认运行在 http://localhost:3001

#### 4. 测试整合功能

```bash
# 进入landlord_agent目录
cd landlord_agent

# 运行整合测试脚本
python voice_landlord_integration_updated.py
```

### API接口说明

#### 1. 语音命令处理接口

**URL**: `/api/process_voice_command`
**方法**: POST
**请求体**:

```json
{
  "audio_text": "玩家A在第一轮出了一张红桃K",
  "timestamp": "2025-12-27T17:52:55.191002"
}
```

**响应**:

```json
{
  "status": "success",
  "parsed_data": {
    "player": "A",
    "round": 1,
    "card": "heart K",
    "weighting": 0.8,
    "original_text": "玩家A在第一轮出了一张红桃K",
    "timestamp": "2025-12-27T17:52:55.191002"
  },
  "ai_decision": {
    "recommended_move": {
      "action": "pass",
      "cards": [],
      "type": "pass"
    }
  }
}
```

#### 2. 语音识别接口

**URL**: `/api/recognize`
**方法**: POST
**请求体**:

```json
{
  "audio_text": "玩家A在第一轮出了一张红桃K",
  "timestamp": "2025-12-27T17:52:55.191002"
}
```

#### 3. 历史记录查询接口

**URL**: `/api/history`
**方法**: GET

#### 4. 健康检查接口

**URL**: `/api/health`
**方法**: GET

### 使用示例

#### Python示例

```python
import requests
import json

# 语音命令
voice_command = "玩家A在第一轮出了一张红桃K"

# 调用API
def call_process_voice_command(voice_text):
    url = "http://localhost:3000/api/process_voice_command"
    data = {
        "audio_text": voice_text,
        "timestamp": "2025-12-27T17:52:55.191002"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.json()

# 获取结果
result = call_process_voice_command(voice_command)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

#### 直接使用整合模块

```python
from landlord_agent.voice_landlord_integration_updated import VoiceLandlordIntegrator

# 创建整合器实例
integrator = VoiceLandlordIntegrator()

# 处理语音命令
voice_text = "玩家A在第一轮出了一张红桃K"
result = integrator.process_voice_command(voice_text)

print(result)
```

### 注意事项

1. 确保已设置正确的Qwen API密钥
2. 语音命令需要符合特定格式："玩家X在第Y轮出了一张Z牌"
3. AI决策基于当前设定的默认手牌，实际应用中需要根据真实游戏状态调整
4. 可以根据需要选择使用Python服务器或Node.js服务器

### 技术栈

- **Python**: 核心编程语言
- **Node.js**: 前端服务器
- **Express**: 构建HTTP服务器
- **http.server**: 构建Python HTTP服务器
- **Qwen-Turbo**: AI决策模型
- **JSON**: 数据交换格式
- **正则表达式**: 语音解析
- **SQLite**: 数据存储

### 未来改进

- 支持更多语音命令格式
- 优化AI决策模型
- 添加更完善的错误处理
- 支持实时语音输入
- 提供更友好的前端界面
- 集成YOLO卡片识别功能
- 完善SQL游戏状态管理
- 实现多智能体决策引擎

### 贡献

欢迎提交Issue和Pull Request，共同改进这个项目！

### 许可证

MIT License
