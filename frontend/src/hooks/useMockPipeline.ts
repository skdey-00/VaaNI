/**
 * useMockPipeline hook
 *
 * Client-side mock pipeline that simulates the entire backend processing chain:
 * 1. Language Identification (LID) from Unicode script ranges
 * 2. ASR (skip - text is already text)
 * 3. Translation to English
 * 4. Named Entity Recognition (NER)
 * 5. LLM Suggestion generation
 *
 * Everything runs entirely client-side with realistic delays.
 * Works 100% offline for hackathon demos.
 */

import { useState, useCallback } from 'react';
import {
  TranscriptEntry,
  Suggestion,
  ProcessGuide,
  BANKING_PROCESS_TEMPLATES,
} from '../types';
import { PipelineStepData } from '../components/PipelineVisualization';

// ============================================================================
// Language Detection from Unicode Script Ranges
// ============================================================================

interface LIDResult {
  language: string;
  languageName: string;
  confidence: number;
  script: string;
}

const SCRIPT_RANGES: { name: string; regex: RegExp; lang: string; langName: string }[] = [
  { name: 'Devanagari', regex: /[\u0900-\u097F]/, lang: 'hi', langName: 'Hindi' },
  { name: 'Tamil', regex: /[\u0B80-\u0BFF]/, lang: 'ta', langName: 'Tamil' },
  { name: 'Telugu', regex: /[\u0C00-\u0C7F]/, lang: 'te', langName: 'Telugu' },
  { name: 'Bengali', regex: /[\u0980-\u09FF]/, lang: 'bn', langName: 'Bengali' },
  { name: 'Kannada', regex: /[\u0C80-\u0CFF]/, lang: 'kn', langName: 'Kannada' },
  { name: 'Malayalam', regex: /[\u0D00-\u0D7F]/, lang: 'ml', langName: 'Malayalam' },
  { name: 'Gujarati', regex: /[\u0A80-\u0AFF]/, lang: 'gu', langName: 'Gujarati' },
];

function detectLanguage(text: string): LIDResult {
  for (const sr of SCRIPT_RANGES) {
    if (sr.regex.test(text)) {
      // Check for Marathi-specific words in Devanagari
      if (sr.name === 'Devanagari') {
        const marathiMarkers = ['आहे', 'आहेत', 'होते', 'करू', 'मला', 'तुम्ही', 'मराठी'];
        const isMarathi = marathiMarkers.some(m => text.includes(m));
        if (isMarathi) {
          return {
            language: 'mr',
            languageName: 'Marathi',
            confidence: 0.91 + Math.random() * 0.06,
            script: 'Devanagari',
          };
        }
      }
      return {
        language: sr.lang,
        languageName: sr.langName,
        confidence: 0.93 + Math.random() * 0.06,
        script: sr.name,
      };
    }
  }

  return {
    language: 'en',
    languageName: 'English',
    confidence: 0.97 + Math.random() * 0.02,
    script: 'Latin',
  };
}

// ============================================================================
// Banking Topic Detection
// ============================================================================

type BankingTopic = 'fd' | 'loan' | 'kyc' | 'account_opening' | 'remittance' | 'complaint' | 'general';

const TOPIC_KEYWORDS: Record<BankingTopic, string[]> = {
  fd: ['fd', 'fixed deposit', 'फिक्स्ड डिपॉजिट', 'एफडी', 'deposit', 'term deposit', 'ब्याज', 'maturity', 'कितने साल', 'interest rate', 'ब्याज दर', 'வட்டி', 'जमा'],
  loan: ['loan', 'लोन', 'கடன்', 'credit', 'emi', 'home loan', 'personal loan', 'car loan', 'education loan', 'ब्याज दर', 'eligibility', 'योग्यता', 'कर्जा'],
  kyc: ['kyc', 'KYC', 'केवाईसी', 'verification', 'पहचान', 'identity', 'document', 'aadhaar', 'आधार', 'pan', 'पैन'],
  account_opening: ['account', 'खाता', 'খাতা', 'account opening', 'नया खाता', 'open account', 'savings', 'current account', 'ఖాతా', 'ಖಾತೆ'],
  remittance: ['transfer', 'ट्रांसफर', 'remittance', 'send money', 'पैसे भेजने', 'NEFT', 'RTGS', 'IMPS', 'बदली', 'fund transfer', 'பணம் அனுப்ப', 'beneficiary'],
  complaint: ['complaint', 'शिकायत', 'problem', 'issue', 'complain', 'गुनागुनी', 'not working', 'blocked', 'बंद', 'deducted', 'कट गया', 'wrong', 'galat', 'புகார்'],
  general: [],
};

function detectBankingTopic(text: string): BankingTopic {
  const lowerText = text.toLowerCase();

  // Score each topic
  let bestTopic: BankingTopic = 'general';
  let bestScore = 0;

  for (const [topic, keywords] of Object.entries(TOPIC_KEYWORDS)) {
    if (topic === 'general') continue;
    let score = 0;
    for (const kw of keywords) {
      if (lowerText.includes(kw.toLowerCase())) {
        score += kw.length; // Longer matches = more specific
      }
    }
    if (score > bestScore) {
      bestScore = score;
      bestTopic = topic as BankingTopic;
    }
  }

  return bestTopic;
}

// ============================================================================
// Translation Dictionaries (simplified mock)
// ============================================================================

const TRANSLATIONS: Record<string, string> = {
  'मुझे फिक्स्ड डिपॉजिट खोलनी है, क्या ब्याज दर बताएंगे?': 'I want to open a fixed deposit. Can you tell me the interest rates?',
  'मुझे लोन लेना है': 'I want to take a loan',
  'मैं अपने खाते का बैलेंस जानना चाहता हूं': 'I want to know my account balance',
  'मेरा एटीएम कार्ड बंद हो गया है': 'My ATM card has been blocked',
  'मुझे पैसे ट्रांसफर करने हैं': 'I need to transfer money',
};

function mockTranslate(text: string, lang: string): string {
  if (lang === 'en') return text;
  if (TRANSLATIONS[text]) return TRANSLATIONS[text];

  // Generic mock: prefix with language note
  const genericTranslations: Record<string, string> = {
    hi: `Customer is inquiring about banking services in Hindi`,
    ta: `Customer is inquiring about banking services in Tamil`,
    te: `Customer is inquiring about banking services in Telugu`,
    bn: `Customer is inquiring about banking services in Bengali`,
    kn: `Customer is inquiring about banking services in Kannada`,
    ml: `Customer is inquiring about banking services in Malayalam`,
    gu: `Customer is inquiring about banking services in Gujarati`,
    mr: `Customer is inquiring about banking services in Marathi`,
  };

  return genericTranslations[lang] || text;
}

// ============================================================================
// Suggestion Generation
// ============================================================================

interface SuggestionSet {
  suggestions: string[];
  processKey: string;
  escalate: boolean;
}

const TOPIC_SUGGESTIONS: Record<BankingTopic, SuggestionSet> = {
  fd: {
    suggestions: [
      'I can help you open a Fixed Deposit. We offer interest rates from 6.5% to 7.2% depending on tenure. Would you like to proceed?',
      'Let me check the current FD interest rates for you. We have special rates for senior citizens as well.',
      'I\'ll need your account number and preferred deposit amount to get started. The minimum FD amount is ₹1,000.',
    ],
    processKey: 'account_opening',
    escalate: false,
  },
  loan: {
    suggestions: [
      'I can help you with a loan application. What type of loan are you looking for — home, personal, or vehicle?',
      'Let me check your eligibility. I\'ll need your income details and employment information to proceed.',
      'Our current personal loan interest rates start from 10.5% p.a. Would you like me to walk you through the application process?',
    ],
    processKey: 'loan_inquiry',
    escalate: false,
  },
  kyc: {
    suggestions: [
      'I can help you complete KYC verification. You\'ll need Aadhaar card and PAN card for this process.',
      'Let me start the biometric verification. Please keep your Aadhaar number ready.',
      'KYC update will be completed in 5-10 minutes. I\'ll guide you through each step.',
    ],
    processKey: 'account_opening',
    escalate: false,
  },
  account_opening: {
    suggestions: [
      'Welcome! I can help you open a new account. Would you prefer a Savings or Current account?',
      'You\'ll need Aadhaar, PAN card, and 2 passport photos for account opening. Do you have these ready?',
      'Let me start the account opening process. First, I need to verify your identity documents.',
    ],
    processKey: 'account_opening',
    escalate: false,
  },
  remittance: {
    suggestions: [
      'I can help you transfer funds. Do you have the beneficiary already added, or would you like to add a new one?',
      'For fund transfer, I\'ll need the beneficiary account number, IFSC code, and transfer amount.',
      'We support NEFT, RTGS, and IMPS transfers. Which method would you prefer based on the urgency?',
    ],
    processKey: 'fund_transfer',
    escalate: false,
  },
  complaint: {
    suggestions: [
      'I understand your concern and apologize for the inconvenience. Let me help resolve this for you immediately.',
      'Let me gather the details of your issue so I can log a complaint and track it to resolution.',
      'I\'ll escalate this to our specialized team for quick resolution. You\'ll receive a tracking number via SMS.',
    ],
    processKey: 'complaint',
    escalate: true,
  },
  general: {
    suggestions: [
      'Thank you for visiting. How can I assist you today? I can help with account services, loans, deposits, and more.',
      'I\'m here to help with any banking queries. Please let me know what you need assistance with.',
      'Feel free to ask about any of our services — accounts, deposits, loans, cards, or transfers.',
    ],
    processKey: 'general',
    escalate: false,
  },
};

// ============================================================================
// NER Mock
// ============================================================================

interface NEREntity {
  text: string;
  label: string;
  start: number;
  end: number;
}

function mockNER(text: string): NEREntity[] {
  const entities: NEREntity[] = [];

  // Detect amounts
  const amountPatterns = [/₹\s*[\d,]+/g, /Rs\.?\s*[\d,]+/gi, /[\d,]+\s*रुपये/g];
  for (const pat of amountPatterns) {
    let match;
    while ((match = pat.exec(text)) !== null) {
      entities.push({ text: match[0], label: 'MONEY', start: match.index, end: match.index + match[0].length });
    }
  }

  // Detect time periods
  const timePatterns = [/\d+\s*(?:year|yr|साल|वर्ष)/gi, /\d+\s*(?:month|महीने)/gi];
  for (const pat of timePatterns) {
    let match;
    while ((match = pat.exec(text)) !== null) {
      entities.push({ text: match[0], label: 'TIME_PERIOD', start: match.index, end: match.index + match[0].length });
    }
  }

  // Detect rates/percentages
  const ratePatterns = [/\d+\.?\d*\s*%/g, /\d+\.?\d*\s*प्रतिशत/g];
  for (const pat of ratePatterns) {
    let match;
    while ((match = pat.exec(text)) !== null) {
      entities.push({ text: match[0], label: 'RATE', start: match.index, end: match.index + match[0].length });
    }
  }

  return entities;
}

// ============================================================================
// Hook Types
// ============================================================================

export interface MockPipelineResult {
  transcript: TranscriptEntry;
  suggestions: Suggestion[];
  processGuide: ProcessGuide;
  pipelineSteps: PipelineStepData[];
  nerEntities: NEREntity[];
  totalTime: number;
}

interface UseMockPipelineReturn {
  isProcessing: boolean;
  pipelineSteps: PipelineStepData[];
  processText: (text: string) => Promise<MockPipelineResult>;
  generateSummary: (transcript: TranscriptEntry[]) => { summaryEn: string; summaryLang: string; queryType: string };
}

// ============================================================================
// Hook Implementation
// ============================================================================

function randomBetween(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function useMockPipeline(): UseMockPipelineReturn {
  const [isProcessing, setIsProcessing] = useState(false);
  const [pipelineSteps, setPipelineSteps] = useState<PipelineStepData[]>([]);

  const processText = useCallback(async (text: string): Promise<MockPipelineResult> => {
    setIsProcessing(true);

    const startTime = Date.now();

    // Initialize pipeline steps
    const steps: PipelineStepData[] = [
      { id: 'lid', label: 'LID', status: 'pending' },
      { id: 'asr', label: 'ASR', status: 'pending' },
      { id: 'translate', label: 'Translate', status: 'pending' },
      { id: 'ner', label: 'NER', status: 'pending' },
      { id: 'llm', label: 'LLM Suggest', status: 'pending' },
    ];

    setPipelineSteps([...steps]);

    // Helper to update a step
    const updateStep = (id: string, status: 'pending' | 'running' | 'completed', duration?: number, detail?: string) => {
      const idx = steps.findIndex(s => s.id === id);
      if (idx !== -1) {
        steps[idx] = { ...steps[idx], status, duration, detail };
        setPipelineSteps([...steps]);
      }
    };

    // ---- Step 1: LID (Language Identification) ----
    updateStep('lid', 'running');
    await delay(randomBetween(120, 280));
    const lidResult = detectLanguage(text);
    updateStep('lid', 'completed', Date.now() - startTime, `${lidResult.languageName} (${lidResult.script})`);

    // ---- Step 2: ASR (skip for text input, but show it for visual) ----
    const asrStart = Date.now();
    updateStep('asr', 'running');
    await delay(randomBetween(80, 200));
    updateStep('asr', 'completed', Date.now() - asrStart, 'Text input - bypassed');

    // ---- Step 3: Translation ----
    const transStart = Date.now();
    updateStep('translate', 'running');
    await delay(randomBetween(100, 250));
    const translatedText = mockTranslate(text, lidResult.language);
    updateStep('translate', 'completed', Date.now() - transStart);

    // ---- Step 4: NER ----
    const nerStart = Date.now();
    updateStep('ner', 'running');
    await delay(randomBetween(30, 80));
    const nerEntities = mockNER(text);
    updateStep('ner', 'completed', Date.now() - nerStart, `${nerEntities.length} entities`);

    // ---- Step 5: LLM Suggestions ----
    const llmStart = Date.now();
    updateStep('llm', 'running');
    await delay(randomBetween(250, 500));

    // Detect topic and get suggestions
    const topic = detectBankingTopic(text);
    const suggestionSet = TOPIC_SUGGESTIONS[topic];
    const processGuide = BANKING_PROCESS_TEMPLATES[suggestionSet.processKey] || BANKING_PROCESS_TEMPLATES.general;

    const suggestions: Suggestion[] = suggestionSet.suggestions.map((text, idx) => ({
      id: `${idx + 1}`,
      text,
      category: topic !== 'general' ? topic.replace('_', ' ').toUpperCase() : undefined,
    }));

    updateStep('llm', 'completed', Date.now() - llmStart, `${suggestions.length} suggestions`);

    // Build transcript entry
    const transcriptEntry: TranscriptEntry = {
      id: `mock-${Date.now()}`,
      role: 'customer',
      originalText: text,
      translatedText: lidResult.language !== 'en' ? translatedText : undefined,
      language: lidResult.language,
      timestamp: new Date(),
      confidence: lidResult.confidence,
    };

    const totalTime = Date.now() - startTime;

    setIsProcessing(false);

    return {
      transcript: transcriptEntry,
      suggestions,
      processGuide,
      pipelineSteps: [...steps],
      nerEntities,
      totalTime,
    };
  }, []);

  const generateSummary = useCallback((transcript: TranscriptEntry[]): { summaryEn: string; summaryLang: string; queryType: string } => {
    // Detect the main topic from all customer messages
    const customerTexts = transcript
      .filter(e => e.role === 'customer')
      .map(e => e.originalText || e.translatedText || '')
      .join(' ');

    const topic = detectBankingTopic(customerTexts);
    const lidResult = detectLanguage(customerTexts);

    const topicNames: Record<BankingTopic, string> = {
      fd: 'Fixed Deposit Inquiry',
      loan: 'Loan Application',
      kyc: 'KYC Verification',
      account_opening: 'Account Opening',
      remittance: 'Fund Transfer / Remittance',
      complaint: 'Customer Complaint',
      general: 'General Inquiry',
    };

    const summariesEn: Record<BankingTopic, string> = {
      fd: `Customer visited the branch to inquire about opening a Fixed Deposit. Discussed interest rates, tenure options, and maturity proceeds. Customer was informed about current FD rates ranging from 6.5% to 7.2%. Process initiated for FD account opening with documentation requirements explained.`,
      loan: `Customer approached for a loan inquiry. Discussed eligibility criteria, required documents, interest rates, and EMI calculations. Customer was guided through the application process and provided with necessary forms. Follow-up scheduled for document collection.`,
      kyc: `Customer requested KYC verification/update. Aadhaar-based biometric verification was completed successfully. PAN details verified. KYC status updated in the system. Customer was informed about the completion and given reference number.`,
      account_opening: `Customer requested opening a new bank account. Discussed account types (Savings/Current), features, and minimum balance requirements. KYC documents were collected and verified. Account opening form was filled. Welcome kit provided to the customer.`,
      remittance: `Customer requested a fund transfer. Beneficiary details were collected and verified. Transfer amount, method (NEFT/RTGS/IMPS), and charges were explained. Transaction was processed successfully and receipt provided to the customer.`,
      complaint: `Customer registered a complaint regarding banking services. Issue was listened to carefully and acknowledged. Relevant details were gathered and logged in the system. Complaint ticket number was provided. Resolution timeline communicated to the customer.`,
      general: `Customer visited the branch with a general inquiry. Query was addressed and relevant information was provided. Customer was satisfied with the assistance and no further action was required.`,
    };

    const summariesLang: Record<BankingTopic, Record<string, string>> = {
      fd: {
        hi: 'ग्राहक ने फिक्स्ड डिपॉजिट खोलने के लिए पूछताछ की। ब्याज दरें, अवधि विकल्प और परिपक्वता राशि पर चर्चा की गई। प्रक्रिया शुरू की गई।',
        ta: 'வாடிக்கையாளர் நிலையான வைப்புத்தொகை திட்டம் பற்றி விசாரித்தார்.',
        en: summariesEn.fd,
      },
      loan: {
        hi: 'ग्राहक ने ऋण के लिए पूछताछ की। पात्रता, ब्याज दरें और EMI पर चर्चा की गई।',
        en: summariesEn.loan,
      },
      kyc: {
        hi: 'ग्राहक ने KYC सत्यापन के लिए अनुरोध किया। आधार-आधारित बायोमेट्रिक सत्यापन पूरा किया गया।',
        en: summariesEn.kyc,
      },
      account_opening: {
        hi: 'ग्राहक ने नया बैंक खाता खोलने का अनुरोध किया। KYC दस्तावेज एकत्र किए गए। खाता खोलने की प्रक्रिया पूरी की गई।',
        en: summariesEn.account_opening,
      },
      remittance: {
        hi: 'ग्राहक ने धन हस्तांतरण का अनुरोध किया। लाभार्थी विवरण सत्यापित किए गए। लेनदेन सफलतापूर्वक संसाधित किया गया।',
        en: summariesEn.remittance,
      },
      complaint: {
        hi: 'ग्राहक ने शिकायत दर्ज की। समस्या को सुना गया और स्वीकार किया गया। शिकायत टिकट जारी किया गया।',
        en: summariesEn.complaint,
      },
      general: {
        hi: 'ग्राहक ने सामान्य पूछताछ के लिए शाखा का दौरा किया। जानकारी प्रदान की गई।',
        en: summariesEn.general,
      },
    };

    const lang = lidResult.language;
    const summaryLang = (summariesLang[topic]?.[lang]) || summariesLang[topic]?.en || summariesEn[topic];

    return {
      summaryEn: summariesEn[topic],
      summaryLang,
      queryType: topicNames[topic],
    };
  }, []);

  return {
    isProcessing,
    pipelineSteps,
    processText,
    generateSummary,
  };
}

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
