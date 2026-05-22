/**
 * PipelineVisualization Component
 *
 * Shows the AI processing pipeline steps with real-time timing.
 * Makes the algorithmic depth visible to hackathon judges.
 * Displays: LID -> ASR -> Translate -> NER -> LLM Suggest
 */

import { CheckCircle, Loader2, Circle, Zap, ArrowRight } from 'lucide-react';

export interface PipelineStepData {
  id: string;
  label: string;
  status: 'pending' | 'running' | 'completed';
  duration?: number; // ms
  detail?: string;
}

interface PipelineVisualizationProps {
  steps: PipelineStepData[];
  totalTime?: number;
  className?: string;
}

export function PipelineVisualization({ steps, totalTime, className = '' }: PipelineVisualizationProps) {
  return (
    <div className={`bg-gray-900 text-white px-4 py-2.5 ${className}`}>
      <div className="flex items-center gap-2 overflow-x-auto">
        {/* Pipeline Label */}
        <div className="flex items-center gap-1.5 mr-2 flex-shrink-0">
          <Zap className="w-3.5 h-3.5 text-yellow-400" />
          <span className="text-xs font-semibold text-yellow-400 uppercase tracking-wider">Pipeline</span>
        </div>

        {/* Steps */}
        {steps.map((step, idx) => (
          <React.Fragment key={step.id}>
            <div className="flex items-center gap-1.5 flex-shrink-0">
              {/* Status Icon */}
              {step.status === 'completed' ? (
                <CheckCircle className="w-3.5 h-3.5 text-green-400 flex-shrink-0" />
              ) : step.status === 'running' ? (
                <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin flex-shrink-0" />
              ) : (
                <Circle className="w-3.5 h-3.5 text-gray-600 flex-shrink-0" />
              )}

              {/* Label */}
              <span
                className={`text-xs font-mono font-semibold whitespace-nowrap ${
                  step.status === 'completed'
                    ? 'text-green-300'
                    : step.status === 'running'
                      ? 'text-blue-300'
                      : 'text-gray-600'
                }`}
              >
                {step.label}
              </span>

              {/* Duration */}
              {step.status === 'completed' && step.duration !== undefined && (
                <span className="text-[10px] font-mono text-green-500 ml-0.5">
                  {step.duration}ms
                </span>
              )}

              {step.status === 'running' && (
                <span className="text-[10px] font-mono text-blue-400 ml-0.5 animate-pulse">
                  ...
                </span>
              )}
            </div>

            {/* Arrow between steps */}
            {idx < steps.length - 1 && (
              <ArrowRight className={`w-3 h-3 flex-shrink-0 ${
                step.status === 'completed' ? 'text-green-600' : 'text-gray-700'
              }`} />
            )}
          </React.Fragment>
        ))}

        {/* Total Time */}
        {totalTime !== undefined && steps.some(s => s.status === 'completed') && (
          <div className="ml-auto flex items-center gap-1.5 flex-shrink-0">
            <span className="text-[10px] text-gray-500">TOTAL</span>
            <span className="text-xs font-mono font-bold text-yellow-300">{totalTime}ms</span>
          </div>
        )}
      </div>
    </div>
  );
}
