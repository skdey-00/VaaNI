/**
 * TextInput Component — Dark Theme
 *
 * Text input area for typing customer queries in any Indian language.
 * Primary demo input for hackathon mode.
 */

import React, { useState, useRef, useEffect } from 'react';
import { Send, Languages, Sparkles } from 'lucide-react';

interface TextInputProps {
  onSubmit: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

const SAMPLE_QUERIES = [
  { text: 'मुझे फिक्स्ड डिपॉजिट खोलनी है, क्या ब्याज दर बताएंगे?', lang: 'Hindi' },
  { text: 'எனக்கு கடன் வேண்டும், என்ன ஆவணங்கள் தேவை?', lang: 'Tamil' },
  { text: 'నా ఖాతాలో డబ్బు బదిలీ చేయాలి', lang: 'Telugu' },
  { text: 'আমি একটি নতুন অ্যাকাউন্ট খুলতে চাই', lang: 'Bengali' },
  { text: 'I want to open a fixed deposit account', lang: 'English' },
];

export function TextInput({ onSubmit, disabled = false, placeholder, className = '' }: TextInputProps) {
  const [text, setText] = useState('');
  const [showSamples, setShowSamples] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [text]);

  const handleSubmit = () => {
    if (text.trim() && !disabled) {
      onSubmit(text.trim());
      setText('');
      setShowSamples(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSampleClick = (sample: string) => {
    setText(sample);
    setShowSamples(false);
    textareaRef.current?.focus();
  };

  return (
    <div className={`bg-zinc-950 border-t border-zinc-800 ${className}`}>
      <div className="p-4">
        {/* Sample Queries Toggle */}
        <div className="flex items-center gap-2 mb-2">
          <button
            onClick={() => setShowSamples(!showSamples)}
            className="flex items-center gap-1.5 text-xs font-medium text-banking-400 hover:text-banking-300 bg-banking-950 hover:bg-banking-900/50 border border-banking-800/50 px-3 py-1.5 rounded-full transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Sample Queries
          </button>
          <div className="flex items-center gap-1 text-xs text-zinc-600">
            <Languages className="w-3.5 h-3.5" />
            Type in any Indian language
          </div>
        </div>

        {/* Sample Queries Dropdown */}
        {showSamples && (
          <div className="mb-3 p-3 bg-zinc-900 border border-zinc-800 rounded-lg space-y-2 animate-slide-in">
            <p className="text-xs font-medium text-zinc-500 mb-2">Click to load a sample query:</p>
            {SAMPLE_QUERIES.map((sample, idx) => (
              <button
                key={idx}
                onClick={() => handleSampleClick(sample.text)}
                className="w-full text-left p-2.5 bg-zinc-950 hover:bg-banking-950/30 border border-zinc-800 hover:border-banking-800/50 rounded-lg text-sm transition-colors group"
              >
                <span className="text-zinc-300 group-hover:text-banking-300">{sample.text}</span>
                <span className="ml-2 text-xs text-zinc-600">({sample.lang})</span>
              </button>
            ))}
          </div>
        )}

        {/* Text Input Area */}
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder || 'Type customer query in any language... (Enter to submit)'}
            disabled={disabled}
            rows={2}
            className="input w-full px-4 py-3 pr-24 resize-none text-base"
            style={{ minHeight: '56px', maxHeight: '120px' }}
            dir="auto"
          />

          {/* Action Buttons */}
          <div className="absolute right-2 bottom-2 flex items-center gap-2">
            <button
              type="button"
              onClick={handleSubmit}
              disabled={disabled || !text.trim()}
              className={`
                px-4 py-2 rounded-lg flex items-center gap-1.5 font-medium text-sm transition-all
                ${text.trim() && !disabled
                  ? 'bg-banking-600 text-white hover:bg-banking-500'
                  : 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                }
              `}
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        </div>

        {/* Helper Text */}
        <div className="mt-1.5 flex items-center justify-between text-xs text-zinc-600">
          <span>
            Press <kbd className="px-1.5 py-0.5 bg-zinc-900 border border-zinc-700 rounded font-mono text-[10px]">Enter</kbd> to submit,
            <kbd className="px-1.5 py-0.5 bg-zinc-900 border border-zinc-700 rounded font-mono text-[10px] ml-1">Shift+Enter</kbd> new line
          </span>
          <span>{text.length} chars</span>
        </div>
      </div>
    </div>
  );
}
