/**
 * Session Page
 *
 * Main layout for active customer session:
 * - TopBar: Full-width at top
 * - Main content: 60% left (TranscriptPanel + ResponseComposer) | 40% right (SuggestionPanel + ProcessGuide)
 * - StatusBar: Bottom
 *
 * Integrates all hooks and components for real-time communication
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useMicrophone } from '../hooks/useMicrophone';
import { useAudioPlayer } from '../hooks/useAudioPlayer';
import { TopBar } from '../components/TopBar';
import { TranscriptPanel } from '../components/TranscriptPanel';
import { SuggestionPanel } from '../components/SuggestionPanel';
import { ProcessGuide } from '../components/ProcessGuide';
import { ResponseComposer } from '../components/ResponseComposer';
import { StatusBar } from '../components/StatusBar';
import {
  TranscriptEntry,
  Suggestion,
  ProcessStep,
  BANKING_PROCESS_TEMPLATES,
  ClientMessage,
} from '../types';

interface SessionPageProps {
  sessionId: string;
  onSessionEnd?: (summary: any) => void;
}

export function SessionPage({ sessionId, onSessionEnd }: SessionPageProps) {
  // State
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en');
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [processGuide, setProcessGuide] = useState(BANKING_PROCESS_TEMPLATES.general);
  const [languageConfidence, setLanguageConfidence] = useState<number | undefined>();
  const [pre_filledResponse, setPre_filledResponse] = useState<string>('');

  // WebSocket connection
  const { status, send, connect, disconnect } = useWebSocket({
    onMessage: handleServerMessage,
    onStatusChange: (newStatus) => {
      console.log('Connection status changed:', newStatus);
    },
  });

  // Microphone recording
  const { recordingState, startRecording, stopRecording, pauseRecording, resumeRecording } =
    useMicrophone({
      onChunk: handleAudioChunk,
      onError: (error) => console.error('Microphone error:', error),
    });

  // Audio player for TTS
  const { play, waveformData } = useAudioPlayer({
    autoPlay: true,
    onPlayEnd: () => console.log('Audio playback ended'),
  });

  // Connect to WebSocket on mount
  useEffect(() => {
    connect(sessionId);
    return () => disconnect();
  }, [sessionId, connect, disconnect]);

  // Send language selection when changed
  useEffect(() => {
    if (status.connected && selectedLanguage) {
      const message: ClientMessage = {
        type: 'language_select',
        language: selectedLanguage,
      };
      send(message);
    }
  }, [selectedLanguage, status.connected, send]);

  // Handle incoming WebSocket messages
  function handleServerMessage(message: any) {
    console.log('Received message:', message);

    switch (message.type) {
      case 'transcript':
        // Add customer transcript
        const newTranscriptEntry: TranscriptEntry = {
          id: `transcript-${Date.now()}`,
          role: 'customer',
          originalText: message.text,
          translatedText: undefined, // Will be filled by translation message
          language: message.language,
          timestamp: new Date(),
          confidence: message.confidence,
        };
        setTranscript((prev) => [...prev, newTranscriptEntry]);
        setLanguageConfidence(message.confidence);
        break;

      case 'translation':
        // Update the last customer transcript with translation
        setTranscript((prev) => {
          const updated = [...prev];
          const lastEntry = updated[updated.length - 1];
          if (lastEntry && lastEntry.role === 'customer') {
            lastEntry.translatedText = message.text;
          }
          return updated;
        });
        break;

      case 'suggestion':
        // Update suggestions and process guide
        const newSuggestions: Suggestion[] = message.suggestions.map((text: string, idx: number) => ({
          id: `suggestion-${idx}`,
          text,
          category: undefined,
        }));
        setSuggestions(newSuggestions);

        // Detect process type from suggestions
        const detectedProcess = detectProcessFromSuggestions(message.suggestions, message.process_steps);
        if (detectedProcess) {
          setProcessGuide(detectedProcess);
        }
        break;

      case 'tts_audio':
        // Play TTS audio
        play(message.audio_b64);
        break;

      case 'lid_result':
        // Update detected language
        setSelectedLanguage(message.language);
        setLanguageConfidence(message.confidence);
        break;

      case 'session_ended':
        // Navigate to summary page
        console.log('Session ended:', message.session_id);
        onSessionEnd?.({ sessionId: message.session_id });
        break;

      case 'error':
        console.error('Server error:', message.message);
        // Could show a toast notification here
        break;

      default:
        console.warn('Unknown message type:', message);
    }
  }

  // Handle audio chunk from microphone
  function handleAudioChunk(chunkBase64: string) {
    const message: ClientMessage = {
      type: 'audio_chunk',
      data: chunkBase64,
    };
    send(message);
  }

  // Detect banking process from AI suggestions
  function detectProcessFromSuggestions(suggestions: string[], steps: string[]): any {
    const text = suggestions.join(' ').toLowerCase() + ' ' + steps.join(' ').toLowerCase();

    if (text.includes('account') && text.includes('open')) {
      return BANKING_PROCESS_TEMPLATES.account_opening;
    } else if (text.includes('loan') || text.includes('credit')) {
      return BANKING_PROCESS_TEMPLATES.loan_inquiry;
    } else if (text.includes('card') || text.includes('debit') || text.includes('atm')) {
      return BANKING_PROCESS_TEMPLATES.card_issue;
    } else if (text.includes('balance') || text.includes('statement')) {
      return BANKING_PROCESS_TEMPLATES.balance_inquiry;
    } else if (text.includes('transfer') || text.includes('send') || text.includes('payment')) {
      return BANKING_PROCESS_TEMPLATES.fund_transfer;
    } else if (text.includes('complaint') || text.includes('issue') || text.includes('problem')) {
      return BANKING_PROCESS_TEMPLATES.complaint;
    }

    return undefined;
  }

  // Handle record button toggle
  const handleRecordToggle = () => {
    if (recordingState.isRecording) {
      if (recordingState.isPaused) {
        resumeRecording();
      } else {
        pauseRecording();
      }
    } else {
      startRecording();
    }
  };

  // Handle staff response send
  const handleSendResponse = useCallback(
    (text: string) => {
      const message: ClientMessage = {
        type: 'staff_response',
        text,
        language: selectedLanguage,
      };
      send(message);

      // Add to transcript
      const staffEntry: TranscriptEntry = {
        id: `staff-${Date.now()}`,
        role: 'staff',
        originalText: text,
        language: 'en',
        timestamp: new Date(),
      };
      setTranscript((prev) => [...prev, staffEntry]);

      setPre_filledResponse('');
    },
    [send, selectedLanguage]
  );

  // Handle suggestion click
  const handleSuggestionClick = (suggestionText: string) => {
    setPre_filledResponse(suggestionText);
  };

  // Handle process step toggle
  const handleStepToggle = (stepId: string) => {
    setProcessGuide((prev) => {
      if (!prev) return prev;

      return {
        ...prev,
        steps: prev.steps.map((step) => {
          if (step.id === stepId && step.active) {
            const newStep = { ...step, completed: !step.completed };

            // Activate next step if this was completed
            if (newStep.completed) {
              const currentIndex = prev.steps.findIndex((s) => s.id === stepId);
              const nextStep = prev.steps[currentIndex + 1];
              if (nextStep) {
                return { ...step, completed: true };
              }
            }

            return newStep;
          }
          return step;
        }).map((step, idx, steps) => {
          // Activate next step after current is completed
          const currentIdx = steps.findIndex((s) => s.id === stepId);
          if (idx === currentIdx + 1 && steps[currentIdx].completed) {
            return { ...step, active: true };
          }
          return step;
        }),
      };
    });
  };

  // Handle new session
  const handleNewSession = () => {
    window.location.reload();
  };

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Top Bar */}
      <TopBar
        selectedLanguage={selectedLanguage}
        onLanguageChange={setSelectedLanguage}
        isRecording={recordingState.isRecording}
        isPaused={recordingState.isPaused}
        onRecordToggle={handleRecordToggle}
        onNewSession={handleNewSession}
        sessionDuration={recordingState.duration}
        isConnected={status.connected}
      />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Column (60%) */}
        <div className="w-3/5 flex flex-col border-r border-gray-200">
          {/* Transcript Panel */}
          <div className="flex-1 overflow-hidden">
            <TranscriptPanel
              transcript={transcript}
              isPlaying={waveformData.length > 0}
            />
          </div>

          {/* Response Composer */}
          <ResponseComposer
            onSend={handleSendResponse}
            placeholder="Type your response here or click a suggestion..."
            disabled={!status.connected}
            prefillType={pre_filledResponse}
          />
        </div>

        {/* Right Column (40%) */}
        <div className="w-2/5 flex flex-col">
          {/* Suggestion Panel */}
          <div className="flex-1 overflow-hidden">
            <SuggestionPanel
              suggestions={suggestions}
              onSuggestionClick={handleSuggestionClick}
              escalate={false}
              loading={status.connected && suggestions.length === 0}
            />
          </div>

          {/* Process Guide */}
          <div className="h-1/2 overflow-hidden">
            <ProcessGuide
              processGuide={processGuide}
              onStepToggle={handleStepToggle}
            />
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <StatusBar
        connectionStatus={status}
        currentLanguage={selectedLanguage}
        languageConfidence={languageConfidence}
        sessionActive={status.connected}
        latency={status.latency}
      />

      {/* Recording Volume Indicator (overlay) */}
      {recordingState.isRecording && !recordingState.isPaused && (
        <div className="fixed bottom-16 left-6 bg-gray-900 bg-opacity-90 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-3">
          <div className="flex gap-1 items-end h-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="w-1 bg-banking-400 rounded"
                style={{
                  height: `${20 + recordingState.volume * 0.8}%`,
                  transition: 'height 50ms ease',
                }}
              />
            ))}
          </div>
          <span className="text-sm font-medium">Recording...</span>
        </div>
      )}
    </div>
  );
}
