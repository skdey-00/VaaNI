/**
 * TranscriptPanel Component — Dark Theme
 *
 * Displays conversation history as chat bubbles:
 * - Customer messages: banking accent, left-aligned, shows original + translation
 * - Staff messages: zinc raised, right-aligned
 * - Auto-scrolls to latest message
 */

import { useEffect, useRef } from 'react';
import { Scroll } from 'lucide-react';
import { TranscriptEntry } from '../types';

interface TranscriptPanelProps {
  transcript: TranscriptEntry[];
  isPlaying?: boolean;
  className?: string;
}

export function TranscriptPanel({ transcript, isPlaying = false, className = '' }: TranscriptPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  const formatTime = (date: Date): string => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    }).format(date);
  };

  return (
    <div className={`bg-zinc-950 flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-zinc-100">Conversation</h2>
          <div className="flex items-center gap-2 text-sm text-zinc-500">
            <Scroll className="w-4 h-4" />
            {transcript.length} messages
          </div>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {transcript.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="w-16 h-16 bg-zinc-900 rounded-full flex items-center justify-center mb-4 border border-zinc-800">
              <Scroll className="w-8 h-8 text-zinc-600" />
            </div>
            <h3 className="text-lg font-medium text-zinc-200 mb-1">No messages yet</h3>
            <p className="text-sm text-zinc-500 max-w-md">
              Start recording or send a message to begin the conversation.
            </p>
          </div>
        ) : (
          transcript.map((entry) => (
            <div
              key={entry.id}
              className={`flex ${entry.role === 'customer' ? 'justify-start' : 'justify-end'}`}
            >
              <div
                className={`max-w-[75%] ${
                  entry.role === 'customer'
                    ? 'bg-banking-950/50 border-banking-800/50'
                    : 'bg-zinc-900 border-zinc-800'
                } border rounded-2xl px-4 py-3 ${
                  entry.role === 'customer' ? 'rounded-tl-sm' : 'rounded-tr-sm'
                }`}
              >
                {/* Role Badge */}
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className={`text-xs font-semibold uppercase tracking-wide ${
                      entry.role === 'customer' ? 'text-banking-400' : 'text-zinc-400'
                    }`}
                  >
                    {entry.role === 'customer' ? 'Customer' : 'You'}
                  </span>
                  {entry.confidence !== undefined && (
                    <span className="text-xs text-zinc-600">
                      {Math.round(entry.confidence * 100)}% conf
                    </span>
                  )}
                  <span className="text-xs text-zinc-600 ml-auto">
                    {formatTime(entry.timestamp)}
                  </span>
                </div>

                {/* Message Content */}
                {entry.role === 'customer' && entry.originalText && entry.originalText !== entry.translatedText ? (
                  <div className="space-y-2">
                    {entry.originalText && (
                      <div className="text-base text-zinc-100 font-medium">
                        {entry.originalText}
                      </div>
                    )}
                    {entry.translatedText && (
                      <div className="text-sm text-zinc-400 border-t border-zinc-800 pt-2 mt-2">
                        {entry.translatedText}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-base text-zinc-200">
                    {entry.originalText || entry.translatedText || 'No text'}
                  </div>
                )}

                {/* Language Badge */}
                <div className="mt-2">
                  <span className="badge-neutral">
                    {entry.language}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={endRef} />
      </div>

      {/* TTS Playing Indicator */}
      {isPlaying && (
        <div className="px-6 py-3 bg-banking-950/30 border-t border-banking-800/30">
          <div className="flex items-center gap-3">
            <div className="flex gap-1 items-end h-6">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="w-1 bg-banking-500 rounded animate-waveform"
                  style={{
                    height: `${50 + Math.random() * 50}%`,
                    animationDelay: `${i * 0.1}s`,
                  }}
                />
              ))}
            </div>
            <span className="text-sm font-medium text-banking-300">Playing audio response...</span>
          </div>
        </div>
      )}
    </div>
  );
}
