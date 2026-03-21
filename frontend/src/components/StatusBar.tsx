/**
 * StatusBar Component
 *
 * Bottom status bar displaying:
 * - Connection status
 * - Latency
 * - Language confidence badge
 * - Active session info
 */

import React from 'react';
import {
  Wifi,
  WifiOff,
  Clock,
  Globe,
  Activity,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react';
import { ConnectionStatus } from '../types';

interface StatusBarProps {
  connectionStatus: ConnectionStatus;
  currentLanguage?: string;
  languageConfidence?: number;
  sessionActive?: boolean;
  latency?: number;
  className?: string;
}

export function StatusBar({
  connectionStatus,
  currentLanguage,
  languageConfidence,
  sessionActive = false,
  latency,
  className = '',
}: StatusBarProps) {
  const getLatencyColor = (ms: number): string => {
    if (ms < 100) return 'text-green-600';
    if (ms < 300) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className={`bg-gray-900 text-gray-300 ${className}`}>
      <div className="px-6 py-2">
        <div className="flex items-center justify-between text-sm">
          {/* Left: Connection Status */}
          <div className="flex items-center gap-6">
            {/* Connection */}
            <div className="flex items-center gap-2">
              {connectionStatus.connected ? (
                <CheckCircle className="w-4 h-4 text-green-500" />
              ) : connectionStatus.connecting ? (
                <Activity className="w-4 h-4 text-yellow-500 animate-pulse" />
              ) : (
                <XCircle className="w-4 h-4 text-red-500" />
              )}
              <span className="font-medium">
                {connectionStatus.connected
                  ? 'Connected'
                  : connectionStatus.connecting
                    ? 'Connecting...'
                    : 'Disconnected'}
              </span>
            </div>

            {/* Session Status */}
            {sessionActive && (
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-banking-400" />
                <span className="text-banking-300 font-medium">Session Active</span>
              </div>
            )}
          </div>

          {/* Center: Language Info */}
          {currentLanguage && (
            <div className="flex items-center gap-6">
              {/* Language */}
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-blue-400" />
                <span>Language: </span>
                <span className="font-medium text-blue-300">{currentLanguage}</span>
              </div>

              {/* Confidence */}
              {languageConfidence !== undefined && (
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-purple-400" />
                  <span>Confidence: </span>
                  <span className={`font-medium ${getConfidenceColor(languageConfidence)}`}>
                    {Math.round(languageConfidence * 100)}%
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Right: Latency */}
          {latency !== undefined && (
            <div className="flex items-center gap-2">
              <Wifi className={`w-4 h-4 ${getLatencyColor(latency)}`} />
              <span>Latency: </span>
              <span className={`font-medium ${getLatencyColor(latency)}`}>
                {latency}ms
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
