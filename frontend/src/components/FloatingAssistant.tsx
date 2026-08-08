import { useState, useRef, useEffect } from 'react';
import { chatAI, getTasks } from '../api';

type Message = {
  role: 'user' | 'ai';
  content: string;
};

export default function FloatingAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const saved = localStorage.getItem('ai_assistant_messages');
      if (saved) return JSON.parse(saved);
    } catch {
      // Ignore
    }
    return [];
  });
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  
  useEffect(() => {
    localStorage.setItem('ai_assistant_messages', JSON.stringify(messages));
  }, [messages]);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleVoiceInput = () => {
    const SpeechRecognitionCtor =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    const recognition = new SpeechRecognitionCtor();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join(' ');

      handleSend(transcript);
    };

    recognition.start();
  };

  const handleSend = async (text: string = input) => {
    if (!text.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    setIsProcessing(true);

    try {
      // Get today's tasks as context
      const tasksData = await getTasks(1, 50).catch(() => null);
      const context = tasksData
        ? tasksData.items.map((t) => ({
            id: t.id,
            title: t.title,
            duration: t.duration,
            is_fixed: t.is_fixed,
            start: t.fixed_start,
          }))
        : [];

      const response = await chatAI(text, context);
      setMessages((prev) => [...prev, { role: 'ai', content: response.reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content:
            'Sorry, I encountered an error while processing that request.',
        },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <>
      <button
        className="floating-ai-button"
        onClick={() => setIsOpen(!isOpen)}
        title="AI Assistant"
      >
        ✨
      </button>

      {isOpen && (
        <div className="floating-chat-window">
          <div className="chat-header">
            <h3>AI Assistant</h3>
            <button className="close-btn" onClick={() => setIsOpen(false)}>
              ✕
            </button>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <p
                style={{
                  textAlign: 'center',
                  color: 'var(--muted)',
                  marginTop: '20px',
                }}
              >
                Hi! Ask me to reschedule or create a task.
              </p>
            )}
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble chat-bubble-${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {isProcessing && (
              <div className="chat-bubble chat-bubble-ai">Thinking...</div>
            )}
            <div ref={chatBottomRef} />
          </div>

          <div className="chat-input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type or speak..."
              disabled={isProcessing}
            />
            <button
              className={`voice-btn ${isListening ? 'listening' : ''}`}
              onClick={handleVoiceInput}
              disabled={isProcessing}
              title="Voice Input"
            >
              🎤
            </button>
          </div>
        </div>
      )}
    </>
  );
}
