import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Trash2, Zap } from 'lucide-react';

const AdminAIChat = ({ token }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Load history from session storage on mount
  useEffect(() => {
    const saved = sessionStorage.getItem('admin_ai_chat');
    if (saved) {
      try {
        setMessages(JSON.parse(saved));
      } catch (e) {}
    } else {
      setMessages([{
        role: 'assistant',
        content: "Assalomu alaykum! Men Somly AI Admin yordamchisiman. Foydalanuvchilar demografiyasi, daromad/xarajat statistikasi yoki reklama segmentlari bo'yicha menga istalgan savolni berishingiz mumkin."
      }]);
    }
  }, []);

  // Save history on change
  useEffect(() => {
    sessionStorage.setItem('admin_ai_chat', JSON.stringify(messages));
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const clearChat = () => {
    if(confirm("Suhbat tarixini o'chirasizmi?")) {
      const initial = [{
        role: 'assistant',
        content: "Assalomu alaykum! Men Somly AI Admin yordamchisiman."
      }];
      setMessages(initial);
      sessionStorage.setItem('admin_ai_chat', JSON.stringify(initial));
    }
  };

  const handleSend = async (textOverride = null) => {
    const text = textOverride || input;
    if (!text.trim() || loading) return;

    const newMessages = [...messages, { role: 'user', content: text.trim() }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/admin/ai-chat/stream', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text.trim(),
          history: messages.slice(-10) // Send last 10 messages as context
        }),
      });

      if (!res.ok) {
        throw new Error(`Server xatosi: ${res.status}`);
      }

      // Add empty assistant message
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      let done = false;
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          setMessages(prev => {
            const updated = [...prev];
            updated[updated.length - 1].content += chunk;
            return updated;
          });
        }
      }
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: `❌ Xatolik: ${e.message}` }]);
    }
    setLoading(false);
  };

  const QUICK_REPLIES = [
    "Toshkentdagi 25-34 yoshli userlar ko'p nima uchun pul sarflaydi?",
    "Qaysi segmentga reklama bersam yaxshi?",
    "Eng faol hududlarni sanab o't"
  ];

  return (
    <div className="admin-page fade-in ai-chat-page">
      <div className="page-header">
        <h1 className="page-title"><Bot size={24} style={{verticalAlign: '-4px', marginRight: '5px'}}/> Somly AI Yordamchi</h1>
        <button className="btn-icon" onClick={clearChat} title="Tozalash"><Trash2 size={18} /></button>
      </div>

      <div className="card chat-container">
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-bubble-wrapper ${msg.role}`}>
              <div className="chat-avatar">
                {msg.role === 'assistant' ? <Bot size={20} /> : <User size={20} />}
              </div>
              <div className="chat-bubble">
                <div className="chat-text">
                  {/* Basic markdown parsing for line breaks and bold */}
                  {msg.content.split('\n').map((line, i) => {
                    // Quick bold parsing
                    const parts = line.split(/(\*\*.*?\*\*)/g);
                    return (
                      <React.Fragment key={i}>
                        {parts.map((part, j) => {
                          if (part.startsWith('**') && part.endsWith('**')) {
                            return <strong key={j}>{part.slice(2, -2)}</strong>;
                          }
                          return part;
                        })}
                        {i !== msg.content.split('\n').length - 1 && <br />}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-bubble-wrapper assistant">
              <div className="chat-avatar"><Bot size={20} /></div>
              <div className="chat-bubble typing">
                <span className="dot"></span><span className="dot"></span><span className="dot"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="quick-replies">
          {QUICK_REPLIES.map((qr, i) => (
            <button key={i} className="qr-btn" onClick={() => handleSend(qr)} disabled={loading}>
              <Zap size={12} color="#f59e0b" /> {qr}
            </button>
          ))}
        </div>

        <div className="chat-input-area">
          <textarea
            className="chat-input"
            placeholder="AI ga savol bering..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={loading}
            rows={1}
          />
          <button className="btn-primary" onClick={() => handleSend()} disabled={loading || !input.trim()}>
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminAIChat;
