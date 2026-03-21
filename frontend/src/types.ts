/**
 * All shared types for the VaaNI frontend
 */

// ============================================================================
// WebSocket Message Types (matching the gateway protocol)
// ============================================================================

export type ClientMessage =
  | AudioChunkMessage
  | LanguageSelectMessage
  | StaffResponseMessage
  | SessionEndMessage;

export type ServerMessage =
  | TranscriptMessage
  | TranslationMessage
  | SuggestionMessage
  | TTSAudioMessage
  | LIDResultMessage
  | ErrorMessage
  | SessionEndedMessage;

// Client → Gateway messages
export interface AudioChunkMessage {
  type: 'audio_chunk';
  data: string; // base64 encoded audio
}

export interface LanguageSelectMessage {
  type: 'language_select';
  language: string;
}

export interface StaffResponseMessage {
  type: 'staff_response';
  text: string;
  language: string;
}

export interface SessionEndMessage {
  type: 'session_end';
}

// Gateway → Client messages
export interface TranscriptMessage {
  type: 'transcript';
  text: string;
  language: string;
  confidence: number;
}

export interface TranslationMessage {
  type: 'translation';
  text: string;
  language: string;
}

export interface SuggestionMessage {
  type: 'suggestion';
  suggestions: string[];
  process_steps: string[];
  escalate: boolean;
}

export interface TTSAudioMessage {
  type: 'tts_audio';
  audio_b64: string;
  language: string;
}

export interface LIDResultMessage {
  type: 'lid_result';
  language: string;
  confidence: number;
}

export interface ErrorMessage {
  type: 'error';
  message: string;
}

export interface SessionEndedMessage {
  type: 'session_ended';
  session_id: string;
}

// ============================================================================
// Application Types
// ============================================================================

export interface TranscriptEntry {
  id: string;
  role: 'customer' | 'staff';
  originalText?: string; // Original language text (for customer)
  translatedText?: string; // English translation
  language: string;
  timestamp: Date;
  confidence?: number;
}

export interface Suggestion {
  id: string;
  text: string;
  category?: string;
}

export interface ProcessStep {
  id: string;
  number: number;
  text: string;
  completed: boolean;
  active: boolean;
}

export interface ProcessGuide {
  id: string;
  name: string;
  steps: ProcessStep[];
}

export interface Session {
  id: string;
  startTime: Date;
  endTime?: Date;
  language: string;
  status: 'connecting' | 'connected' | 'ended' | 'error';
  transcript: TranscriptEntry[];
  currentSuggestions: Suggestion[];
  currentProcessGuide?: ProcessGuide;
  summary?: SessionSummary;
}

export interface SessionSummary {
  summaryEn: string;
  summaryLang: string;
  queryType: string;
  transcript: TranscriptEntry[];
}

export interface ConnectionStatus {
  connected: boolean;
  connecting: boolean;
  error?: string;
  latency?: number;
}

export interface RecordingState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
}

export interface AudioPlayback {
  isPlaying: boolean;
  volume: number;
}

// ============================================================================
// Language Options
// ============================================================================

export interface LanguageOption {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
}

export const LANGUAGES: LanguageOption[] = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇬🇧' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी', flag: '🇮🇳' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', flag: '🇮🇳' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', flag: '🇮🇳' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', flag: '🇮🇳' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', flag: '🇮🇳' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', flag: '🇮🇳' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', flag: '🇮🇳' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', flag: '🇮🇳' },
  { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪' },
  { code: 'zh', name: 'Chinese', nativeName: '中文', flag: '🇨🇳' },
  { code: 'ar', name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português', flag: '🇵🇹' },
];

// ============================================================================
// Banking Process Templates
// ============================================================================

export const BANKING_PROCESS_TEMPLATES: Record<string, ProcessGuide> = {
  account_opening: {
    id: 'account_opening',
    name: 'Account Opening',
    steps: [
      { id: '1', number: 1, text: 'Verify customer identity (KYC documents)', completed: false, active: true },
      { id: '2', number: 2, text: 'Check account type requirements', completed: false, active: false },
      { id: '3', number: 3, text: 'Fill account opening form', completed: false, active: false },
      { id: '4', number: 4, text: 'Complete biometric verification', completed: false, active: false },
      { id: '5', number: 5, text: 'Initial deposit & welcome kit', completed: false, active: false },
    ],
  },
  loan_inquiry: {
    id: 'loan_inquiry',
    name: 'Loan Inquiry',
    steps: [
      { id: '1', number: 1, text: 'Understand loan requirement', completed: false, active: true },
      { id: '2', number: 2, text: 'Check eligibility criteria', completed: false, active: false },
      { id: '3', number: 3, text: 'Explain interest rates & terms', completed: false, active: false },
      { id: '4', number: 4, text: 'Collect required documents', completed: false, active: false },
      { id: '5', number: 5, text: 'Submit application', completed: false, active: false },
    ],
  },
  card_issue: {
    id: 'card_issue',
    name: 'Debit/Credit Card Issue',
    steps: [
      { id: '1', number: 1, text: 'Verify account status', completed: false, active: true },
      { id: '2', number: 2, text: 'Choose card type', completed: false, active: false },
      { id: '3', number: 3, text: 'Fill card application form', completed: false, active: false },
      { id: '4', number: 4, text: 'Complete KYC verification', completed: false, active: false },
      { id: '5', number: 5, text: 'Generate PIN & deliver card', completed: false, active: false },
    ],
  },
  balance_inquiry: {
    id: 'balance_inquiry',
    name: 'Balance Inquiry',
    steps: [
      { id: '1', number: 1, text: 'Verify customer identity', completed: false, active: true },
      { id: '2', number: 2, text: 'Check account balance', completed: false, active: false },
      { id: '3', number: 3, text: 'Provide mini statement', completed: false, active: false },
      { id: '4', number: 4, text: 'Explain any charges or deductions', completed: false, active: false },
    ],
  },
  fund_transfer: {
    id: 'fund_transfer',
    name: 'Fund Transfer',
    steps: [
      { id: '1', number: 1, text: 'Get beneficiary details', completed: false, active: true },
      { id: '2', number: 2, text: 'Verify transfer limits', completed: false, active: false },
      { id: '3', number: 3, text: 'Authenticate transaction', completed: false, active: false },
      { id: '4', number: 4, text: 'Process transfer', completed: false, active: false },
      { id: '5', number: 5, text: 'Provide transaction receipt', completed: false, active: false },
    ],
  },
  complaint: {
    id: 'complaint',
    name: 'Complaint / Dispute',
    steps: [
      { id: '1', number: 1, text: 'Listen to customer complaint', completed: false, active: true },
      { id: '2', number: 2, text: 'Acknowledge and empathize', completed: false, active: false },
      { id: '3', number: 3, text: 'Gather relevant details', completed: false, active: false },
      { id: '4', number: 4, text: 'Log complaint in system', completed: false, active: false },
      { id: '5', number: 5, text: 'Provide ticket number & timeline', completed: false, active: false },
    ],
  },
  general: {
    id: 'general',
    name: 'General Inquiry',
    steps: [
      { id: '1', number: 1, text: 'Understand customer query', completed: false, active: true },
      { id: '2', number: 2, text: 'Provide accurate information', completed: false, active: false },
      { id: '3', number: 3, text: 'Check if customer needs more help', completed: false, active: false },
    ],
  },
};

// ============================================================================
// Mock Data for Development
// ============================================================================

export function createMockTranscript(): TranscriptMessage {
  const mockTexts = [
    { text: 'मैं अपने खाते का बैलेंस जानना चाहता हूं', lang: 'hi', conf: 0.95 },
    { text: 'मुझे लोन लेना है', lang: 'hi', conf: 0.92 },
    { text: 'यह कितने समय में मिलेगा', lang: 'hi', conf: 0.88 },
    { text: 'मेरा एटीएम कार्ड बंद हो गया है', lang: 'hi', conf: 0.91 },
  ];
  const random = mockTexts[Math.floor(Math.random() * mockTexts.length)];
  return {
    type: 'transcript',
    text: random.text,
    language: random.lang,
    confidence: random.conf,
  };
}

export function createMockTranslation(): TranslationMessage {
  return {
    type: 'translation',
    text: 'I want to know my account balance',
    language: 'en',
  };
}

export function createMockSuggestions(): SuggestionMessage {
  const suggestions = [
    'I can check your account balance right away. May I have your account number?',
    'I can help you with that. Please provide your customer ID for verification.',
    'Would you like me to also show you your recent transactions?',
  ];
  return {
    type: 'suggestion',
    suggestions: suggestions.slice(0, Math.floor(Math.random() * 3) + 1),
    process_steps: ['Account verification', 'Balance inquiry'],
    escalate: false,
  };
}

export function createMockLID(): LIDResultMessage {
  const languages = ['hi', 'mr', 'ta', 'te', 'bn'];
  const lang = languages[Math.floor(Math.random() * languages.length)];
  return {
    type: 'lid_result',
    language: lang,
    confidence: 0.9 + Math.random() * 0.1,
  };
}
