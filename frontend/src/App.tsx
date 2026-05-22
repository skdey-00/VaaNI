/**
 * App.tsx
 *
 * Main application component.
 * Handles session creation and routing between Session, Summary, and Metrics pages.
 * Supports demo mode via URL param ?demo=true
 */

import { useState, useEffect } from 'react';
import { SessionPage } from './pages/Session';
import { SummaryPage } from './pages/Summary';
import { MetricsPage } from './pages/Metrics';
import { SessionSummary } from './types';

type AppState = 'loading' | 'session' | 'summary' | 'metrics';

const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true';

function App() {
  const [appState, setAppState] = useState<AppState>('loading');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionSummary, setSessionSummary] = useState<SessionSummary | null>(null);
  const [demoPreload, setDemoPreload] = useState(false);

  useEffect(() => {
    // Check for demo mode in URL
    const params = new URLSearchParams(window.location.search);
    if (params.get('demo') === 'true') {
      setDemoPreload(true);
    }
    createSession();
  }, []);

  async function createSession() {
    try {
      console.log('Creating new session...');

      if (MOCK_MODE) {
        const mockSessionId = 'mock-session-' + Date.now();
        setSessionId(mockSessionId);
        setAppState('session');
        console.log('Mock session created:', mockSessionId);
        return;
      }

      const response = await fetch('http://localhost:8000/session/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) throw new Error('Failed to create session');

      const data = await response.json();
      setSessionId(data.session_id);
      setAppState('session');
      console.log('Session created:', data.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
      if (MOCK_MODE) {
        setSessionId('mock-session-fallback');
        setAppState('session');
        return;
      }
      setTimeout(createSession, 3000);
    }
  }

  function handleSessionEnd(summary: any) {
    if (summary && summary.summaryEn) {
      setSessionSummary(summary);
    }
    setAppState('summary');
  }

  function handleNewSession() {
    setSessionId(null);
    setSessionSummary(null);
    setAppState('loading');
    createSession();
  }

  if (appState === 'loading') {
    return (
      <div className="h-screen flex items-center justify-center bg-zinc-950">
        <div className="text-center">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-zinc-700 border-t-blue-500 mx-auto" />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-lg font-bold text-blue-400">V</span>
            </div>
          </div>
          <h2 className="mt-4 text-xl font-semibold text-white">VaaNI</h2>
          <p className="text-sm text-zinc-500 mt-1">Voice Assistant for New India</p>
        </div>
      </div>
    );
  }

  if (appState === 'metrics') {
    return <MetricsPage onBack={() => setAppState('session')} />;
  }

  if (appState === 'summary' && sessionId) {
    return (
      <SummaryPage
        sessionId={sessionId}
        onNewSession={handleNewSession}
        mockSummary={sessionSummary}
      />
    );
  }

  if (appState === 'session' && sessionId) {
    return (
      <SessionPage
        sessionId={sessionId}
        onSessionEnd={handleSessionEnd}
        onShowMetrics={() => setAppState('metrics')}
        demoPreload={demoPreload}
      />
    );
  }

  return null;
}

export default App;
