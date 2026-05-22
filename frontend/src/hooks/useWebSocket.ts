/**
 * useWebSocket hook
 *
 * Manages WebSocket connection to the gateway service.
 * Features:
 * - Auto-reconnection with exponential backoff
 * - Message queuing while connecting
 * - Mock mode for development (no-op - mock pipeline is used instead)
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
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const messageQueueRef = useRef<ClientMessage[]>([]);
  const pingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastPongRef = useRef<number>(Date.now());

  // In mock mode, just mark as connected and don't do anything
  const startMockMode = useCallback(() => {
    console.log('🎭 Mock mode: WebSocket replaced by client-side mock pipeline');
    setStatus({ connected: true, connecting: false, latency: 0 });
    onStatusChange?.({ connected: true, connecting: false, latency: 0 });
  }, [onStatusChange]);

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

    // Start mock mode if enabled - no actual WebSocket
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
