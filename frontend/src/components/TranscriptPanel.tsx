/**
 * TranscriptPanel Component
 *
 * Displays conversation history as chat bubbles:
 * - Customer messages: Blue, left-aligned, shows original + translation
 * - Staff messages: Gray, right-aligned
 * - Auto-scrolls to latest message
 * - Smooth animations for new messages
 */

import React, { useEffect, useRef } from 'react';
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

  // Auto-scroll to bottom when new messages arrive
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
    <div className={`bg-white flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Conversation</h2>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Scroll className="w-4 h-4" />
            {transcript.length} messages
          </div>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {transcript.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Scroll className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-1">No messages yet</h3>
            <p className="text-sm text-gray-500 max-w-md">
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
                    ? 'bg-blue-50 border-blue-200'
                    : 'bg-gray-100 border-gray-200'
                } border-2 rounded-2xl px-4 py-3 ${
                  entry.role === 'customer' ? 'rounded-tl-sm' : 'rounded-tr-sm'
                }`}
              >
                {/* Role Badge */}
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className={`text-xs font-semibold uppercase tracking-wide ${
                      entry.role === 'customer' ? 'text-blue-600' : 'text-gray-600'
                    }`}
                  >
                    {entry.role === 'customer' ? 'Customer' : 'You'}
                  </span>
                  {entry.confidence !== undefined && (
                    <span className="text-xs text-gray-400">
                      {Math.round(entry.confidence * 100)}% conf
                    </span>
                  )}
                  <span className="text-xs text-gray-400 ml-auto">
                    {formatTime(entry.timestamp)}
                  </span>
                </div>

                {/* Message Content */}
                {entry.role === 'customer' && entry.originalText && entry.originalText !== entry.translatedText ? (
                  <div className="space-y-2">
                    {/* Original Language */}
                    {entry.originalText && (
                      <div className="text-base text-gray-800 font-medium">
                        {entry.originalText}
                      </div>
                    )}
                    {/* English Translation */}
                    {entry.translatedText && (
                      <div className="text-sm text-gray-600 border-t border-gray-200 pt-2 mt-2">
                        {entry.translatedText}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-base text-gray-800">
                    {entry.originalText || entry.translatedText || 'No text'}
                  </div>
                )}

                {/* Language Badge */}
                <div className="mt-2">
                  <span className="text-xs text-gray-500">
                    Language: <span className="font-medium">{entry.language}</span>
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
        <div className="px-6 py-3 bg-purple-50 border-t border-purple-200">
          <div className="flex items-center gap-3">
            <div className="flex gap-1 items-end h-6">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="w-1 bg-purple-500 rounded animate-waveform"
                  style={{
                    height: `${50 + Math.random() * 50}%`,
                    animationDelay: `${i * 0.1}s`,
                  }}
                />
              ))}
            </div>
            <span className="text-sm font-medium text-purple-700">Playing audio response...</span>
          </div>
        </div>
      )}
    </div>
  );
}
