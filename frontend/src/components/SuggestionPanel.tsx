/**
 * SuggestionPanel Component — Dark Theme
 *
 * Displays AI-powered response suggestions as clickable cards.
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
    <div className={`bg-zinc-950 flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-5 py-4 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-amber-400" />
          <h2 className="text-lg font-semibold text-zinc-100">AI Suggestions</h2>
        </div>
        <p className="text-sm text-zinc-500 mt-1">
          Click a suggestion to use it
        </p>
      </div>

      {/* Escalation Warning */}
      {escalate && (
        <div className="mx-5 mt-4 p-3 bg-red-950/50 border border-red-800/50 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-red-300">Escalation Recommended</h3>
              <p className="text-xs text-red-400 mt-1">
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
                className="p-4 bg-zinc-900 border border-zinc-800 rounded-lg animate-pulse"
              >
                <div className="h-4 bg-zinc-800 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-zinc-800 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        ) : suggestions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-8">
            <div className="w-12 h-12 bg-zinc-900 rounded-full flex items-center justify-center mb-3 border border-zinc-800">
              <Lightbulb className="w-6 h-6 text-zinc-600" />
            </div>
            <h3 className="text-sm font-medium text-zinc-300 mb-1">No suggestions yet</h3>
            <p className="text-xs text-zinc-500 max-w-xs">
              Speak with the customer to generate AI-powered response suggestions.
            </p>
          </div>
        ) : (
          suggestions.map((suggestion) => (
            <button
              key={suggestion.id}
              onClick={() => onSuggestionClick(suggestion.text)}
              className="w-full text-left p-4 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-banking-700 rounded-lg transition-all group"
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 bg-banking-600 text-white rounded-full flex items-center justify-center text-sm font-bold group-hover:scale-110 transition-transform">
                  {suggestion.id}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-zinc-200 group-hover:text-banking-300 transition-colors">
                    {suggestion.text}
                  </p>
                  {suggestion.category && (
                    <span className="inline-block mt-2 text-xs font-medium text-banking-400 bg-banking-950 border border-banking-800 px-2 py-1 rounded">
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
      <div className="px-5 py-3 bg-zinc-900 border-t border-zinc-800">
        <p className="text-xs text-zinc-500 text-center">
          Suggestions are based on customer query and conversation context
        </p>
      </div>
    </div>
  );
}
