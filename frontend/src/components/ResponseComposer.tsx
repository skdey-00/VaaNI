/**
 * ResponseComposer Component
 *
 * Text input area for staff responses:
 * - Staff can type free-form responses
 * - Or click a suggestion to populate
 * - Send button transmits via WebSocket
 * - Character counter
 */

import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, X } from 'lucide-react';

interface ResponseComposerProps {
  onSend: (text: string) => void;
  placeholder?: string;
  disabled?: boolean;
  prefillType?: string;
  className?: string;
}

export function ResponseComposer({
  onSend,
  placeholder = 'Type your response here...',
  disabled = false,
  prefillType,
  className = '',
}: ResponseComposerProps) {
  const [text, setText] = useState('');
  const [isSuggestion, setIsSuggestion] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-populate from suggestion
  useEffect(() => {
    if (prefillType) {
      setText(prefillType);
      setIsSuggestion(true);
      textareaRef.current?.focus();
    }
  }, [prefillType]);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, [text]);

  const handleSend = () => {
    if (text.trim()) {
      onSend(text.trim());
      setText('');
      setIsSuggestion(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearSuggestion = () => {
    setText('');
    setIsSuggestion(false);
  };

  const charCount = text.length;
  const maxChars = 1000;

  return (
    <div className={`bg-white border-t border-gray-200 ${className}`}>
      <div className="p-4">
        {/* Suggestion Badge */}
        {isSuggestion && (
          <div className="flex items-center justify-between mb-2 px-3 py-2 bg-banking-50 border border-banking-200 rounded-lg">
            <span className="text-sm font-medium text-banking-700">
              💡 AI suggestion loaded
            </span>
            <button
              onClick={clearSuggestion}
              className="p-1 hover:bg-banking-100 rounded transition-colors"
            >
              <X className="w-4 h-4 text-banking-600" />
            </button>
          </div>
        )}

        {/* Text Area */}
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={`
              w-full px-4 py-3 pr-24 border-2 border-gray-200 rounded-lg
              focus:outline-none focus:ring-2 focus:ring-banking-500 focus:border-transparent
              disabled:bg-gray-100 disabled:cursor-not-allowed resize-none
              transition-shadow
            `}
            style={{ minHeight: '48px', maxHeight: '150px' }}
          />

          {/* Action Buttons */}
          <div className="absolute right-2 bottom-2 flex items-center gap-2">
            {/* Character Count */}
            <span
              className={`
                text-xs font-medium mr-1
                ${charCount > maxChars * 0.9 ? 'text-red-500' : 'text-gray-400'}
              `}
            >
              {charCount}/{maxChars}
            </span>

            {/* Attachment Button (future feature) */}
            <button
              type="button"
              disabled={disabled}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Attach file (coming soon)"
            >
              <Paperclip className="w-5 h-5" />
            </button>

            {/* Send Button */}
            <button
              type="button"
              onClick={handleSend}
              disabled={disabled || !text.trim()}
              className={`
                p-2 rounded-lg flex items-center gap-1.5 font-medium transition-all
                ${text.trim() && !disabled
                  ? 'bg-banking-600 text-white hover:bg-banking-700'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                }
              `}
            >
              <Send className="w-4 h-4" />
              <span className="text-sm">Send</span>
            </button>
          </div>
        </div>

        {/* Helper Text */}
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          <span>
            Press <kbd className="px-1.5 py-0.5 bg-gray-100 rounded font-mono">Enter</kbd> to send,
            <kbd className="px-1.5 py-0.5 bg-gray-100 rounded font-mono ml-1">Shift + Enter</kbd> for new line
          </span>
        </div>
      </div>
    </div>
  );
}
