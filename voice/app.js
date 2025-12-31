class VoiceRecognitionApp {
    constructor() {
        this.recognition = null;
        this.isRecording = false;
        this.currentTranscript = '';
        this.currentResult = null;

        this.initializeSpeechRecognition();
        this.bindEvents();
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
        } else if ('SpeechRecognition' in window) {
            this.recognition = new SpeechRecognition();
        } else {
            this.showToast('您的浏览器不支持语音识别，请使用Chrome浏览器', 'error');
            this.disableMicButton();
            return;
        }

        this.recognition.lang = 'zh-CN';
        this.recognition.continuous = true;
        this.recognition.interimResults = true;

        this.recognition.onstart = () => {
            this.isRecording = true;
            this.updateMicButton(true);
            this.updateMicStatus('正在聆听...');
        };

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (finalTranscript) {
                this.currentTranscript += finalTranscript;
                this.updateTranscript(this.currentTranscript);
                this.processVoiceInput(finalTranscript);
            } else {
                this.updateTranscript(this.currentTranscript + interimTranscript);
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.handleRecognitionError(event.error);
        };

        this.recognition.onend = () => {
            if (this.isRecording) {
                this.recognition.start();
            }
        };
    }

    handleRecognitionError(error) {
        const errorMessages = {
            'no-speech': '未检测到语音，请重试',
            'audio-capture': '未找到麦克风设备',
            'not-allowed': '麦克风权限被拒绝',
            'network': '网络错误，请检查连接',
            'aborted': '语音识别被中断',
            'language-not-supported': '不支持该语言',
            'service-not-allowed': '语音服务被拒绝'
        };

        const message = errorMessages[error] || `语音识别错误: ${error}`;
        this.showToast(message, 'error');
        this.stopRecording();
    }

    bindEvents() {
        const micButton = document.getElementById('micButton');
        const copyButton = document.getElementById('copyButton');
        const clearButton = document.getElementById('clearButton');

        micButton.addEventListener('click', () => this.toggleRecording());
        copyButton.addEventListener('click', () => this.copyResult());
        clearButton.addEventListener('click', () => this.clearResult());
    }

    toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }

    startRecording() {
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Failed to start recognition:', error);
            this.showToast('启动语音识别失败，请重试', 'error');
        }
    }

    stopRecording() {
        this.isRecording = false;
        this.recognition.stop();
        this.updateMicButton(false);
        this.updateMicStatus('点击开始语音输入');
    }

    updateMicButton(active) {
        const micButton = document.getElementById('micButton');
        if (active) {
            micButton.classList.add('active');
        } else {
            micButton.classList.remove('active');
        }
    }

    updateMicStatus(message) {
        const statusElement = document.getElementById('micStatus');
        statusElement.textContent = message;
    }

    updateTranscript(text) {
        const speechText = document.getElementById('speechText');
        speechText.textContent = text || '请开始说话...';
    }

    async processVoiceInput(text) {
        if (!text.trim()) return;

        this.showToast('正在识别...', 'loading');
        this.updateApiStatus('loading');

        try {
            const response = await fetch('/api/recognize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    audio_text: text,
                    timestamp: new Date().toISOString()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.currentResult = data;
            this.displayResult(data);
            this.updateApiStatus('success');
            this.showToast('识别完成', 'success');

        } catch (error) {
            console.error('Recognition error:', error);
            this.updateApiStatus('error');
            this.showToast('识别失败，请重试', 'error');
        }
    }

    displayResult(data) {
        const resultContent = document.getElementById('resultContent');

        const timestamp = new Date(data.timestamp).toLocaleString('zh-CN');

        if (data.error) {
            resultContent.innerHTML = `
                <div class="result-item error">
                    <div class="result-label">解析失败</div>
                    <div class="result-value">${this.escapeHtml(data.error)}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">原始文本</div>
                    <div class="result-value">${this.escapeHtml(data.original_text || '')}</div>
                </div>
                <div class="result-meta">
                    <span>识别时间: ${timestamp}</span>
                </div>
            `;
            this.enableResultButtons();
            return;
        }

        const suitNames = {
            'heart': '红桃',
            'spade': '黑桃',
            'club': '梅花',
            'diamond': '方片'
        };

        const cardDisplay = data.card ? data.card : '未识别';
        const cardParts = data.card ? data.card.split(' ') : [];
        const suitName = cardParts.length >= 2 ? suitNames[cardParts[0]] || cardParts[0] : '';
        const rankName = cardParts.length >= 2 ? cardParts[1] : '';

        const html = `
            <div class="result-item">
                <div class="result-label">玩家</div>
                <div class="result-value player">${this.escapeHtml(data.player || '')}</div>
            </div>
            <div class="result-item">
                <div class="result-label">轮次</div>
                <div class="result-value round">第 ${this.escapeHtml((data.round || '').toString())} 轮</div>
            </div>
            <div class="result-item">
                <div class="result-label">扑克牌</div>
                <div class="result-value card">
                    ${suitName}${rankName}
                    <span class="card-raw">(${cardDisplay})</span>
                </div>
            </div>
            <div class="result-item">
                <div class="result-label">原始文本</div>
                <div class="result-value">${this.escapeHtml(data.original_text || '')}</div>
            </div>
            <div class="result-meta">
                <span>识别时间: ${timestamp}</span>
            </div>
        `;

        resultContent.innerHTML = html;
        this.enableResultButtons();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    enableResultButtons() {
        const copyButton = document.getElementById('copyButton');
        const clearButton = document.getElementById('clearButton');
        copyButton.disabled = false;
        clearButton.disabled = false;
    }

    disableMicButton() {
        const micButton = document.getElementById('micButton');
        micButton.disabled = true;
        micButton.style.opacity = '0.5';
        micButton.style.cursor = 'not-allowed';
    }

    copyResult() {
        if (!this.currentResult) return;

        if (this.currentResult.error) {
            navigator.clipboard.writeText(this.currentResult.original_text || '').then(() => {
                this.showToast('已复制到剪贴板', 'success');
            }).catch(() => {
                this.showToast('复制失败', 'error');
            });
            return;
        }

        const textToCopy = `玩家: ${this.currentResult.player}\n轮次: 第${this.currentResult.round}轮\n扑克牌: ${this.currentResult.card}`;
        navigator.clipboard.writeText(textToCopy).then(() => {
            this.showToast('已复制到剪贴板', 'success');
        }).catch(() => {
            this.showToast('复制失败', 'error');
        });
    }

    clearResult() {
        this.currentTranscript = '';
        this.currentResult = null;
        this.updateTranscript('请开始说话...');

        const resultContent = document.getElementById('resultContent');
        resultContent.innerHTML = `
            <div class="placeholder">
                <svg viewBox="0 0 100 100" width="60" height="60">
                    <circle cx="50" cy="50" r="45" fill="none" stroke="#00d4ff" stroke-width="2" opacity="0.3"/>
                    <path d="M35 50 L45 50 L50 40 L55 60 L60 50 L65 50" fill="none" stroke="#00d4ff" stroke-width="3" opacity="0.5"/>
                </svg>
                <p>等待语音输入...</p>
            </div>
        `;

        const copyButton = document.getElementById('copyButton');
        const clearButton = document.getElementById('clearButton');
        copyButton.disabled = true;
        clearButton.disabled = true;

        this.updateApiStatus('ready');
        this.showToast('已清除', 'success');
    }

    updateApiStatus(status) {
        const apiStatus = document.getElementById('apiStatus');
        apiStatus.className = 'api-status';

        const statusMessages = {
            'ready': '就绪',
            'loading': '处理中...',
            'success': '识别成功',
            'error': '识别失败'
        };

        apiStatus.classList.add(status);
        apiStatus.textContent = statusMessages[status] || status;
    }

    showToast(message, type = 'info') {
        let toast = document.querySelector('.toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.className = 'toast';
            document.body.appendChild(toast);
        }

        toast.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new VoiceRecognitionApp();
});