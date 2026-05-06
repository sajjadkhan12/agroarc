
import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal, HelpCircle } from 'lucide-react';
import { ChatMessage } from '../types';

interface ChatPanelProps {
  onCommand: (command: string, params: Record<string, string>, rawInput: string) => void;
  messages: ChatMessage[];
  isLoading?: boolean;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ onCommand, messages, isLoading = false }) => {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const parts = input.trim().split(/\s+/);
    const cmd = parts[0].toLowerCase();
    const params: Record<string, string> = {};

    parts.slice(1).forEach(part => {
      const [key, val] = part.split('=');
      if (key && val) params[key] = val;
    });

    onCommand(cmd, params, input.trim());
    setInput('');
  };

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 flex flex-col h-[500px] overflow-hidden shadow-2xl">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-indigo-400" />
          <span className="font-semibold text-slate-200">AgroArc Command Tester</span>
        </div>
        <div className="group relative">
          <HelpCircle className="w-4 h-4 text-slate-500 cursor-help" />
          <div className="absolute right-0 top-6 w-64 bg-slate-800 text-slate-300 text-[10px] p-3 rounded-lg invisible group-hover:visible z-50 border border-slate-700 shadow-xl leading-relaxed">
            <p className="font-bold text-slate-100 mb-1">Commands:</p>
            <p>• crop N=90 P=42 K=43 temp=25 humidity=80 ph=6.5 rainfall=200</p>
            <p className="mt-1">• weather city=London</p>
            <p className="mt-1">• fertilizer temp=26 humidity=70 moisture=40 soil=Sandy crop=Wheat N=20 P=10 K=15</p>
            <p className="mt-2 text-indigo-300">• Or type normal text for general AI chat</p>
          </div>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-3 rounded-2xl text-sm ${
              msg.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-none' 
                : 'bg-slate-800 text-slate-300 border border-slate-700 rounded-tl-none font-mono'
            }`}>
              {msg.content}
              <div className="text-[10px] mt-1 opacity-50 block">
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-[85%] p-3 rounded-2xl text-sm bg-slate-800 text-slate-300 border border-slate-700 rounded-tl-none font-mono">
              Thinking...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-800 bg-slate-900/50">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type command or ask anything..."
            disabled={isLoading}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg py-2 pl-4 pr-12 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
          />
          <button 
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 top-1.5 p-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 text-white rounded-md transition-all shadow-lg"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
