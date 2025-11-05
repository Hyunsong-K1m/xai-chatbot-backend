// app/services/XAIChatbotAPI.js
// React Native 앱에서 사용할 API 클라이언트

class XAIChatbotAPI {
  constructor() {
    // 개발 서버 URL (실제 서버 URL로 변경 필요)
    this.baseURL = 'http://192.168.1.100:8000'; // 로컬 IP 사용
    // this.baseURL = '<내꺼 URL 적기>'; // 프로덕션 URL
    
    this.apiPath = '/api/v1/mobile';
    this.sessionId = null;
    this.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }

  // API 호출 헬퍼 함수
  async apiCall(endpoint, options = {}) {
    const url = `${this.baseURL}${this.apiPath}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.headers,
          ...options.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || error.error || 'API call failed');
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // 헬스 체크
  async checkHealth() {
    return this.apiCall('/health');
  }

  // 새 세션 생성
  async createSession(userId = null) {
    const response = await this.apiCall('/session', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        metadata: {
          platform: 'mobile',
          app_version: '1.0.0',
        }
      }),
    });

    if (response.success) {
      this.sessionId = response.session_id;
    }

    return response;
  }

  // 채팅 메시지 전송
  async sendMessage(message, sessionId = null) {
    // 세션 ID가 없으면 자동 생성
    if (!sessionId && !this.sessionId) {
      await this.createSession();
    }

    const response = await this.apiCall('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: message,
        session_id: sessionId || this.sessionId,
        context: {
          timestamp: new Date().toISOString(),
        }
      }),
    });

    return response;
  }

  // 채팅 히스토리 가져오기
  async getChatHistory(sessionId = null, limit = 50) {
    const sid = sessionId || this.sessionId;
    if (!sid) {
      throw new Error('Session ID is required');
    }

    return this.apiCall(`/session/${sid}/history?limit=${limit}`);
  }

  // RAG 검색
  async ragSearch(query, topK = 5) {
    return this.apiCall('/rag/query', {
      method: 'POST',
      body: JSON.stringify({
        query: query,
        top_k: topK,
        session_id: this.sessionId,
      }),
    });
  }

  // 세션 삭제
  async deleteSession(sessionId = null) {
    const sid = sessionId || this.sessionId;
    if (!sid) {
      throw new Error('Session ID is required');
    }

    const response = await this.apiCall(`/session/${sid}`, {
      method: 'DELETE',
    });

    if (response.success && sid === this.sessionId) {
      this.sessionId = null;
    }

    return response;
  }

  // 활성 세션 목록 (관리자용)
  async listSessions(userId = null) {
    const params = userId ? `?user_id=${userId}` : '';
    return this.apiCall(`/sessions${params}`);
  }

  // 세션 ID 설정/가져오기
  getSessionId() {
    return this.sessionId;
  }

  setSessionId(sessionId) {
    this.sessionId = sessionId;
  }

  // 로컬 스토리지에서 세션 복구
  async restoreSession(storedSessionId) {
    try {
      const history = await this.getChatHistory(storedSessionId, 1);
      if (history.success) {
        this.sessionId = storedSessionId;
        return true;
      }
    } catch (error) {
      console.log('Session not found, creating new one');
    }
    return false;
  }
}

// 사용 예제
/*
import XAIChatbotAPI from './services/XAIChatbotAPI';

const api = new XAIChatbotAPI();

// 컴포넌트에서 사용
const ChatScreen = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    initializeChat();
  }, []);

  const initializeChat = async () => {
    try {
      // 세션 생성
      await api.createSession('user123');
      
      // 이전 대화 불러오기
      const history = await api.getChatHistory();
      if (history.success) {
        setMessages(history.messages);
      }
    } catch (error) {
      console.error('Failed to initialize chat:', error);
    }
  };

  const sendMessage = async (text) => {
    setLoading(true);
    try {
      const response = await api.sendMessage(text);
      if (response.success) {
        setMessages(prev => [...prev, 
          { role: 'user', content: text },
          response.message
        ]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    // UI 컴포넌트
  );
};
*/

export default XAIChatbotAPI;