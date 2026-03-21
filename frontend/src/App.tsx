/**
 * App.tsx
 *
 * Main application component.
 * Handles session creation and routing between Session and Summary pages.
 */

import React, { useState, useEffect } from 'react';
import { SessionPage } from './pages/Session';
import { SummaryPage } from './pages/Summary';
import { Loader2 } from 'lucide-react';

type AppState = 'loading' | 'session' | 'summary';

function App() {
  const [appState, setAppState] = useState<AppState>('loading');
  const [sessionId, setSessionId] = useState<string | null>(null);

  useEffect(() => {
    // Create a new session on app load
    createSession();
  }, []);

  async function createSession() {
    try {
      console.log('Creating new session...');

      if (import.meta.env.VITE_MOCK_MODE === 'true') {
        // In mock mode, generate a fake session ID
        const mockSessionId = 'mock-session-' + Date.now();
        setSessionId(mockSessionId);
        setAppState('session');
        console.log('Mock session created:', mockSessionId);
        return;
      }

      const response = await fetch('http://localhost:8000/session/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to create session');
      }

      const data = await response.json();
      setSessionId(data.session_id);
      setAppState('session');
      console.log('Session created:', data.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);

      // For development, show a helpful error message
      if (import.meta.env.DEV) {
        console.warn(`
          ⚠️ Failed to connect to gateway service.
          Make sure the gateway is running on http://localhost:8000
          Or set VITE_MOCK_MODE=true in .env for mock mode
        `);
      }

      // Retry after 3 seconds
      setTimeout(createSession, 3000);
    }
  }

  function handleSessionEnd(summary: any) {
    setAppState('summary');
  }

  function handleNewSession() {
    setSessionId(null);
    setAppState('loading');
    createSession();
  }

  if (appState === 'loading') {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-banking-50 to-blue-50">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-banking-600 mx-auto"></div>
            <Loader2 className="absolute top-0 left-0 w-16 h-16 text-banking-600 animate-pulse" />
          </div>
          <h1 className="mt-6 text-2xl font-bold text-gray-900">VaaNI</h1>
          <p className="mt-2 text-gray-600">Voice Assistant for New India</p>
          <p className="mt-4 text-sm text-gray-500">
            {sessionId ? 'Connecting to session...' : 'Creating session...'}
          </p>
          {!sessionId && (
            <p className="mt-2 text-xs text-gray-400">
              Make sure the gateway service is running on port 8000
            </p>
          )}
        </div>
      </div>
    );
  }

  if (appState === 'session' && sessionId) {
    return <SessionPage sessionId={sessionId} onSessionEnd={handleSessionEnd} />;
  }

  if (appState === 'summary' && sessionId) {
    return <SummaryPage sessionId={sessionId} onNewSession={handleNewSession} />;
  }

  return null;
}

export default App;
