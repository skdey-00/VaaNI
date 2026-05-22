/**
 * SuggestionPanel Component
 *
 * Displays AI-powered response suggestions as clickable cards.
 * - Shows 2-3 LLM suggestions
 * - Clicking populates the response composer
 * - Shows escalation warning if needed
 */

import { Lightbulb, AlertTriangle } from 'lucide-react';
import { Suggestion } from '../types';

interface SuggestionPanelProps {
  suggestions: Suggestion[];
  onSuggestionClick: (suggestion: string) => void;
  escalate?: boolean;
  loading?: boolean;
  className?: string;
}

export function SuggestionPanel({
  suggestions,
  onSuggestionClick,
  escalate = false,
  loading = false,
  className = '',
}: SuggestionPanelProps) {
  return (
    <div className={`bg-white flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-500" />
          <h2 className="text-lg font-semibold text-gray-900">AI Suggestions</h2>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          Click a suggestion to use it
        </p>
      </div>

      {/* Escalation Warning */}
      {escalate && (
        <div className="mx-5 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-red-800">Escalation Recommended</h3>
              <p className="text-xs text-red-700 mt-1">
                This query may require supervisor assistance
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Suggestions List */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="p-4 bg-gray-50 border border-gray-200 rounded-lg animate-pulse"
              >
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : suggestions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-8">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-3">
              <Lightbulb className="w-6 h-6 text-gray-400" />
            </div>
            <h3 className="text-sm font-medium text-gray-900 mb-1">No suggestions yet</h3>
            <p className="text-xs text-gray-500 max-w-xs">
              Speak with the customer to generate AI-powered response suggestions.
            </p>
          </div>
        ) : (
          suggestions.map((suggestion) => (
            <button
              key={suggestion.id}
              onClick={() => onSuggestionClick(suggestion.text)}
              className="w-full text-left p-4 bg-gradient-to-r from-banking-50 to-blue-50 hover:from-banking-100 hover:to-blue-100 border-2 border-banking-200 hover:border-banking-300 rounded-lg transition-all group"
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 bg-banking-500 text-white rounded-full flex items-center justify-center text-sm font-bold group-hover:scale-110 transition-transform">
                  {suggestion.id}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 group-hover:text-banking-700 transition-colors">
                    {suggestion.text}
                  </p>
                  {suggestion.category && (
                    <span className="inline-block mt-2 text-xs font-medium text-banking-600 bg-banking-100 px-2 py-1 rounded">
                      {suggestion.category}
                    </span>
                  )}
                </div>
              </div>
            </button>
          ))
        )}
      </div>

      {/* Footer Tip */}
      <div className="px-5 py-3 bg-gray-50 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          💡 Suggestions are based on customer query and conversation context
        </p>
      </div>
    </div>
  );
}
