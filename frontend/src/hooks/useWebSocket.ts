/**
 * useWebSocket hook
 *
 * Manages WebSocket connection to the gateway service.
 * Features:
 * - Auto-reconnection with exponential backoff
 * - Message queuing while connecting
 * - Mock mode for development
 * - Typed send/receive API
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { ServerMessage, ClientMessage } from '../types';

const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (message: ServerMessage) => void;
  onStatusChange?: (status: ConnectionStatus) => void;
}

interface ConnectionStatus {
  connected: boolean;
  connecting: boolean;
  error?: string;
  latency?: number;
}

interface UseWebSocketReturn {
  lastMessage: ServerMessage | null;
  status: ConnectionStatus;
  send: (message: ClientMessage) => void;
  connect: (sessionId: string) => void;
  disconnect: () => void;
  sessionId: string | null;
}

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    autoConnect = false,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    onMessage,
    onStatusChange,
  } = options;

  const [lastMessage, setLastMessage] = useState<ServerMessage | null>(null);
  const [status, setStatus] = useState<ConnectionStatus>({
    connected: false,
    connecting: false,
  });
  const [sessionId, setSessionId] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const messageQueueRef = useRef<ClientMessage[]>([]);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastPongRef = useRef<number>(Date.now());

  // Mock message generator for development
  const startMockMode = useCallback(() => {
    console.log('🎭 Mock mode enabled - simulating WebSocket messages');

    // Simulate connecting
    setStatus({ connected: true, connecting: false });
    onStatusChange?.({ connected: true, connecting: false });

    // Simulate messages periodically
    const mockInterval = setInterval(() => {
      if (Math.random() > 0.7) {
        // Randomly send different message types
        const rand = Math.random();
        let mockMessage: ServerMessage;

        if (rand < 0.3) {
          const { createMockTranscript } = await import('../types');
          mockMessage = createMockTranscript();
        } else if (rand < 0.5) {
          const { createMockTranslation } = await import('../types');
          mockMessage = createMockTranslation();
        } else if (rand < 0.7) {
          const { createMockSuggestions } = await import('../types');
          mockMessage = createMockSuggestions();
        } else if (rand < 0.85) {
          const { createMockLID } = await import('../types');
          mockMessage = createMockLID();
        } else {
          // TTS audio
          mockMessage = {
            type: 'tts_audio',
            audio_b64: btoa('mock audio data'),
            language: 'en',
          };
        }

        setLastMessage(mockMessage);
        onMessage?.(mockMessage);
      }
    }, 2000);

    return () => clearInterval(mockInterval);
  }, [onMessage, onStatusChange]);

  // Send queued messages
  const flushQueue = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN && messageQueueRef.current.length > 0) {
      console.log(`📤 Sending ${messageQueueRef.current.length} queued messages`);

      messageQueueRef.current.forEach((message) => {
        wsRef.current?.send(JSON.stringify(message));
      });

      messageQueueRef.current = [];
    }
  }, []);

  // Calculate latency
  const measureLatency = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const start = Date.now();
      wsRef.current.send(JSON.stringify({ type: 'ping' }));

      const timeout = setTimeout(() => {
        const latency = Date.now() - start;
        setStatus((prev) => ({ ...prev, latency }));
        onStatusChange?.({ ...status, latency });
      }, 100);

      return () => clearTimeout(timeout);
    }
  }, [status, onStatusChange]);

  // WebSocket message handler
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: ServerMessage = JSON.parse(event.data);

      // Handle pong response for latency measurement
      if (message && typeof message === 'object' && 'type' in message) {
        if ((message as any).type === 'pong') {
          lastPongRef.current = Date.now();
          return;
        }
      }

      setLastMessage(message);
      onMessage?.(message);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }, [onMessage]);

  // WebSocket connection
  const connect = useCallback((newSessionId: string) => {
    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Start mock mode if enabled
    if (MOCK_MODE) {
      setSessionId(newSessionId);
      startMockMode();
      return;
    }

    const wsUrl = `ws://localhost:8000/ws/${newSessionId}`;
    console.log(`🔌 Connecting to ${wsUrl}`);

    setStatus({ connected: false, connecting: true });
    onStatusChange?.({ connected: false, connecting: true });

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      setSessionId(newSessionId);
      reconnectAttemptsRef.current = 0;

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setStatus({ connected: true, connecting: false });
        onStatusChange?.({ connected: true, connecting: false });
        reconnectAttemptsRef.current = 0;

        // Send queued messages
        flushQueue();

        // Start ping interval for latency measurement
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        pingIntervalRef.current = window.setInterval(measureLatency, 30000);
      };

      ws.onmessage = handleMessage;

      ws.onerror = (event) => {
        console.error('❌ WebSocket error:', event);
        setStatus((prev) => ({
          ...prev,
          connecting: false,
          error: 'WebSocket connection error',
        }));
        onStatusChange?.({
          connected: false,
          connecting: false,
          error: 'WebSocket connection error',
        });
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket closed');

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        setStatus({ connected: false, connecting: false });
        onStatusChange?.({ connected: false, connecting: false });

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const delay = reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1);

          console.log(
            `🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );

          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
          }

          reconnectTimeoutRef.current = setTimeout(() => {
            if (sessionId) {
              connect(sessionId);
            }
          }, delay);
        } else {
          console.error('❌ Max reconnection attempts reached');
          setStatus((prev) => ({
            ...prev,
            error: 'Max reconnection attempts reached',
          }));
          onStatusChange?.({
            connected: false,
            connecting: false,
            error: 'Max reconnection attempts reached',
          });
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setStatus({
        connected: false,
        connecting: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
      onStatusChange?.({
        connected: false,
        connecting: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }, [
    sessionId,
    reconnectInterval,
    maxReconnectAttempts,
    flushQueue,
    handleMessage,
    measureLatency,
    onStatusChange,
    startMockMode,
  ]);

  // Disconnect WebSocket
  const disconnect = useCallback(() => {
    console.log('🔌 Disconnecting WebSocket');

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setSessionId(null);
    setStatus({ connected: false, connecting: false });
    onStatusChange?.({ connected: false, connecting: false });
  }, [onStatusChange]);

  // Send message
  const send = useCallback((message: ClientMessage) => {
    if (MOCK_MODE) {
      console.log('📤 [MOCK] Sending message:', message);
      return;
    }

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.log('📥 Queueing message (not connected):', message);
      messageQueueRef.current.push(message);
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, [disconnect]);

  return {
    lastMessage,
    status,
    send,
    connect,
    disconnect,
    sessionId,
  };
}
