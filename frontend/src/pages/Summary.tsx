/**
 * Summary Page
 *
 * Post-session summary page showing:
 * - Bilingual summary in two columns
 * - Query type, resolved/escalated status chips
 * - Full conversation log as scrollable table
 * - PDF export functionality
 * - CBS integration stub
 * - Mock mode: works entirely client-side
 */

import { useState, useEffect } from 'react';
import {
  Download,
  FileText,
  Calendar,
  Clock,
  Globe,
  Tag,
  Home,
  FileDown,
  CheckCircle,
  XCircle,
  MessageSquare,
  Send,
  X,
} from 'lucide-react';
import { TranscriptEntry, SessionSummary } from '../types';

const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true';

interface SummaryPageProps {
  sessionId: string;
  onNewSession: () => void;
  mockSummary?: SessionSummary | null;
}

interface TranscriptRow {
  id: string;
  time: string;
  speaker: 'Customer' | 'Staff';
  originalText: string;
  translatedText: string;
  language: string;
}

export function SummaryPage({ sessionId, onNewSession, mockSummary }: SummaryPageProps) {
  const [summary, setSummary] = useState<SessionSummary | null>(null);
  const [transcript, setTranscript] = useState<TranscriptRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [toast, setToast] = useState<{ show: boolean; message: string; type: 'success' | 'error' }>({
    show: false,
    message: '',
    type: 'success',
  });

  useEffect(() => {
    if (MOCK_MODE && mockSummary) {
      // Use mock summary directly
      setSummary(mockSummary);
      const rows: TranscriptRow[] = mockSummary.transcript.map((entry: TranscriptEntry, idx: number) => ({
        id: `transcript-${idx}`,
        time: new Date(entry.timestamp).toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: true,
        }),
        speaker: entry.role === 'customer' ? 'Customer' : 'Staff',
        originalText: entry.originalText || '',
        translatedText: entry.translatedText || (entry.role === 'staff' ? entry.originalText || '' : ''),
        language: entry.language,
      }));
      setTranscript(rows);
      setLoading(false);
    } else {
      fetchSummary();
      fetchTranscript();
    }
  }, [sessionId, mockSummary]);

  async function fetchSummary() {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/session/${sessionId}/end`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to fetch summary');
      const data = await response.json();
      setSummary({
        summaryEn: data.summary_en,
        summaryLang: data.summary_lang,
        queryType: data.query_type,
        transcript: [],
      });
    } catch (error) {
      console.error('Failed to fetch summary:', error);
      showToast('Failed to load summary', 'error');
    } finally {
      setLoading(false);
    }
  }

  async function fetchTranscript() {
    try {
      const response = await fetch(`http://localhost:8000/session/${sessionId}/transcript`);
      if (!response.ok) throw new Error('Failed to fetch transcript');
      const data = await response.json();
      const rows: TranscriptRow[] = (data.transcript || []).map((entry: any, idx: number) => ({
        id: `transcript-${idx}`,
        time: new Date(entry.timestamp).toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: true,
        }),
        speaker: entry.role,
        originalText: entry.text,
        translatedText: entry.role === 'customer' ? '' : entry.text,
        language: entry.language,
      }));
      setTranscript(rows);
    } catch (error) {
      console.error('Failed to fetch transcript:', error);
    }
  }

  async function handleExportPDF() {
    setExporting(true);
    try {
      if (MOCK_MODE) {
        // In mock mode, export JSON instead
        handleExportJSON();
        return;
      }
      const response = await fetch(`http://localhost:8000/session/${sessionId}/export/pdf`);
      if (!response.ok) throw new Error('Failed to generate PDF');
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `vaani_session_${sessionId}.pdf`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="(.+)"/);
        if (match) filename = match[1];
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      showToast('PDF exported successfully', 'success');
    } catch (error) {
      console.error('PDF export failed:', error);
      showToast('Failed to export PDF', 'error');
    } finally {
      setExporting(false);
    }
  }

  async function handleExportJSON() {
    setExporting(true);
    try {
      const data = {
        sessionId,
        date: new Date().toISOString(),
        summary: summary,
        transcript: transcript,
      };
      const content = JSON.stringify(data, null, 2);
      const filename = `vaani_session_${sessionId}.json`;
      const blob = new Blob([content], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      showToast('JSON exported successfully', 'success');
    } catch (error) {
      console.error('JSON export failed:', error);
      showToast('Failed to export JSON', 'error');
    } finally {
      setExporting(false);
    }
  }

  function handlePushToCBS() {
    console.log('Pushing to CBS:', { sessionId, summary, transcript });
    setTimeout(() => {
      showToast('Successfully pushed to Core Banking System', 'success');
    }, 500);
  }

  function showToast(message: string, type: 'success' | 'error') {
    setToast({ show: true, message, type });
    setTimeout(() => {
      setToast((prev) => ({ ...prev, show: false }));
    }, 3000);
  }

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-banking-600 mx-auto mb-4"></div>
          <p className="text-lg font-medium text-gray-700">Loading summary...</p>
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Summary Not Available</h2>
          <p className="text-gray-600 mb-6">Unable to load session summary</p>
          <button
            onClick={onNewSession}
            className="px-6 py-3 bg-banking-600 text-white rounded-lg font-medium hover:bg-banking-700 transition-colors"
          >
            Start New Session
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {toast.show && (
        <div
          className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-6 py-4 rounded-lg shadow-lg animate-slide-in ${
            toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
          } text-white`}
        >
          {toast.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
          <span className="font-medium">{toast.message}</span>
          <button onClick={() => setToast((prev) => ({ ...prev, show: false }))} className="ml-2 hover:opacity-80">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      <div className="bg-white border-b border-gray-200 shadow-sm no-print">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Session Summary</h1>
              <p className="text-sm text-gray-500 mt-1">Review and export conversation details</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handlePushToCBS}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors"
              >
                <Send className="w-4 h-4" />
                Push to CBS
              </button>
              <button
                onClick={onNewSession}
                className="flex items-center gap-2 px-5 py-2 bg-banking-600 text-white rounded-lg font-medium hover:bg-banking-700 transition-colors"
              >
                <Home className="w-4 h-4" />
                New Session
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6 no-print">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600">Date:</span>
                  <span className="font-medium text-gray-900">{new Date().toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600">Session ID:</span>
                  <span className="font-medium text-gray-900 font-mono">{sessionId.slice(0, 8)}...</span>
                </div>
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600">Messages:</span>
                  <span className="font-medium text-gray-900">{transcript.length}</span>
                </div>
                {MOCK_MODE && (
                  <div className="flex items-center gap-2 px-3 py-1 bg-purple-100 rounded-full">
                    <span className="text-xs font-medium text-purple-700">Demo Mode</span>
                  </div>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleExportJSON}
                  disabled={exporting}
                  className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  <Download className="w-4 h-4" />
                  JSON
                </button>
                <button
                  onClick={handleExportPDF}
                  disabled={exporting}
                  className="flex items-center gap-2 px-4 py-2 bg-banking-600 text-white rounded-lg text-sm font-medium hover:bg-banking-700 transition-colors disabled:opacity-50"
                >
                  <FileDown className="w-4 h-4" />
                  {exporting ? 'Generating...' : 'Export'}
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-banking-100 rounded-lg flex items-center justify-center">
                  <Tag className="w-5 h-5 text-banking-600" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-500 uppercase font-semibold">Query Type</p>
                  <p className="text-lg font-bold text-gray-900 mt-1">{summary.queryType}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-500 uppercase font-semibold">Resolution</p>
                  <p className="text-lg font-bold text-green-700 mt-1">Resolved</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <XCircle className="w-5 h-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-500 uppercase font-semibold">Escalation</p>
                  <p className="text-lg font-bold text-blue-700 mt-1">Not Escalated</p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 bg-blue-50">
                <div className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-banking-600" />
                  <h2 className="text-lg font-semibold text-gray-900">English Summary</h2>
                </div>
              </div>
              <div className="p-6">
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">{summary.summaryEn}</p>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 bg-yellow-50">
                <div className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-yellow-600" />
                  <h2 className="text-lg font-semibold text-gray-900">Local Language Summary</h2>
                </div>
              </div>
              <div className="p-6">
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">{summary.summaryLang}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-gray-600" />
                  <h2 className="text-lg font-semibold text-gray-900">Conversation Log</h2>
                </div>
                <span className="text-sm text-gray-500">{transcript.length} messages</span>
              </div>
            </div>
            <div className="overflow-x-auto max-h-96 overflow-y-auto">
              <table className="w-full">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Time</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Speaker</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider w-2/5">Original Text</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider w-2/5">English Translation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {transcript.map((row) => (
                    <tr key={row.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.time}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          row.speaker === 'Customer' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {row.speaker}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{row.originalText}</td>
                      <td className="px-6 py-4 text-sm text-gray-600 italic">{row.translatedText || '\u2014'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {transcript.length === 0 && (
                <div className="text-center py-12">
                  <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No conversation log available</p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 no-print">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Staff Notes</h3>
            <textarea
              placeholder="Add any additional notes about this session..."
              className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-banking-500 focus:border-transparent resize-none"
            />
            <div className="mt-3 flex justify-end">
              <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
                Save Notes
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border-t border-gray-200 px-6 py-3 no-print">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-gray-500">
          <span>Generated by VaaNI \u2014 Confidential Banking Record</span>
          <span>{new Date().toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}
