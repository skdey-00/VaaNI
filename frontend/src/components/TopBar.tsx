/**
 * TopBar Component — Dark Theme
 *
 * Top navigation bar containing:
 * - Language selector with Indian language names and script previews
 * - Session timer
 * - Record/Pause button with flashing red dot indicator
 * - New session button
 * - Connection status indicator
 * - Load Demo button (hackathon)
 */

import { useState, useEffect } from 'react';
import { Mic, Square, RotateCcw, Wifi, WifiOff, Clock, Zap, BarChart3 } from 'lucide-react';
import { LANGUAGES } from '../types';

const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true';

interface TopBarProps {
  selectedLanguage: string;
  onLanguageChange: (language: string) => void;
  isRecording: boolean;
  isPaused: boolean;
  onRecordToggle: () => void;
  onNewSession: () => void;
  onLoadDemo?: () => void;
  onShowMetrics?: () => void;
  sessionDuration: number;
  isConnected: boolean;
  isProcessing?: boolean;
  className?: string;
}

export function TopBar({
  selectedLanguage,
  onLanguageChange,
  isRecording,
  isPaused,
  onRecordToggle,
  onNewSession,
  onLoadDemo,
  onShowMetrics,
  sessionDuration,
  isConnected,
  isProcessing = false,
  className = '',
}: TopBarProps) {
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isRecording && !isPaused) {
      interval = setInterval(() => {
        setDuration((d) => d + 1);
      }, 1000);
    } else if (!isRecording) {
      setDuration(0);
    }
    return () => clearInterval(interval);
  }, [isRecording, isPaused]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`bg-zinc-950 border-b border-zinc-800 ${className}`}>
      <div className="px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Left: Language Selector & Timer */}
          <div className="flex items-center gap-4">
            {/* Language Selector */}
            <div className="flex items-center gap-2">
              <label htmlFor="language-select" className="text-sm font-medium text-zinc-400">
                Language
              </label>
              <select
                id="language-select"
                value={selectedLanguage}
                onChange={(e) => onLanguageChange(e.target.value)}
                disabled={isRecording}
                className="input text-sm font-medium min-w-[180px] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {LANGUAGES.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.nativeName} ({lang.name})
                  </option>
                ))}
              </select>
            </div>

            {/* Session Timer */}
            <div className="flex items-center gap-2 px-3 py-2 bg-zinc-900 rounded-lg border border-zinc-800">
              <Clock className="w-4 h-4 text-zinc-500" />
              <span className="text-sm font-mono font-medium text-zinc-300">
                {formatTime(duration)}
              </span>
            </div>

            {/* Connection Status */}
            <div className="flex items-center gap-2">
              {isConnected ? (
                <div className="flex items-center gap-1.5 text-emerald-400">
                  <Wifi className="w-4 h-4" />
                  <span className="text-xs font-medium">{MOCK_MODE ? 'Demo Mode' : 'Connected'}</span>
                </div>
              ) : (
                <div className="flex items-center gap-1.5 text-red-400">
                  <WifiOff className="w-4 h-4" />
                  <span className="text-xs font-medium">Disconnected</span>
                </div>
              )}
            </div>
          </div>

          {/* Right: Recording Controls & Buttons */}
          <div className="flex items-center gap-3">
            {/* Load Demo Button (Mock mode only) */}
            {MOCK_MODE && onLoadDemo && (
              <button
                onClick={onLoadDemo}
                disabled={isProcessing}
                className="flex items-center gap-2 px-4 py-2.5 bg-banking-600 hover:bg-banking-500 text-white rounded-lg font-medium transition-all shadow-lg shadow-banking-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Zap className="w-4 h-4" />
                Load Demo
              </button>
            )}

            {/* Metrics Button */}
            {onShowMetrics && (
              <button
                onClick={onShowMetrics}
                className="btn-secondary"
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                Metrics
              </button>
            )}

            {/* Recording Button */}
            <button
              onClick={onRecordToggle}
              disabled={!isConnected}
              className={`
                relative flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium text-white transition-all
                ${isRecording
                  ? isPaused
                    ? 'bg-amber-600 hover:bg-amber-500'
                    : 'bg-red-600 hover:bg-red-500 animate-pulse-fast'
                  : 'bg-banking-600 hover:bg-banking-500'
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            >
              {/* Flashing Red Dot */}
              {isRecording && !isPaused && (
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                </span>
              )}

              {isRecording ? (
                isPaused ? (
                  <>
                    <Mic className="w-5 h-5" />
                    Resume
                  </>
                  ) : (
                    <>
                      <Square className="w-5 h-5" />
                      Stop
                    </>
                  )
              ) : (
                <>
                  <Mic className="w-5 h-5" />
                  Record
                </>
              )}
            </button>

            {/* New Session Button */}
            <button
              onClick={onNewSession}
              className="btn-ghost"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              New Session
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
