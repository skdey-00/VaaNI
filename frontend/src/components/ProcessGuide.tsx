/**
 * ProcessGuide Component — Dark Theme
 *
 * Displays step-by-step checklist for the current banking process.
 */

import { Check, Circle, ListChecks } from 'lucide-react';
import { ProcessGuide as ProcessGuideType } from '../types';

interface ProcessGuideProps {
  processGuide: ProcessGuideType | undefined;
  onStepToggle: (stepId: string) => void;
  className?: string;
}

export function ProcessGuide({
  processGuide,
  onStepToggle,
  className = '',
}: ProcessGuideProps) {
  if (!processGuide) {
    return (
      <div className={`bg-zinc-950 flex flex-col ${className}`}>
        <div className="px-5 py-4 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <ListChecks className="w-5 h-5 text-banking-500" />
            <h2 className="text-lg font-semibold text-zinc-100">Process Guide</h2>
          </div>
        </div>

        <div className="flex-1 flex items-center justify-center p-6">
          <p className="text-sm text-zinc-500 text-center">
            Process guide will appear based on customer inquiry
          </p>
        </div>
      </div>
    );
  }

  const completedCount = processGuide.steps.filter((s) => s.completed).length;
  const progress = (completedCount / processGuide.steps.length) * 100;

  return (
    <div className={`bg-zinc-950 flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-5 py-4 border-b border-zinc-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ListChecks className="w-5 h-5 text-banking-500" />
            <h2 className="text-lg font-semibold text-zinc-100">{processGuide.name}</h2>
          </div>
          <span className="text-sm font-medium text-banking-400">
            {completedCount}/{processGuide.steps.length}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="mt-3">
          <div className="w-full bg-zinc-800 rounded-full h-2">
            <div
              className="bg-banking-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Steps List */}
      <div className="flex-1 overflow-y-auto px-5 py-4">
        <div className="space-y-2">
          {processGuide.steps.map((step) => (
            <button
              key={step.id}
              onClick={() => onStepToggle(step.id)}
              disabled={step.active}
              className={`
                w-full text-left p-4 rounded-lg border transition-all group
                ${step.completed
                  ? 'bg-emerald-950/30 border-emerald-800/40 hover:bg-emerald-950/50'
                  : step.active
                    ? 'bg-banking-950/30 border-banking-700/50 shadow-sm shadow-banking-600/10'
                    : 'bg-zinc-900 border-zinc-800 hover:bg-zinc-800'
                }
                ${step.active ? 'cursor-pointer' : 'cursor-default'}
              `}
            >
              <div className="flex items-start gap-3">
                {/* Step Number / Checkbox */}
                <div className="flex-shrink-0">
                  {step.completed ? (
                    <div className="w-7 h-7 bg-emerald-600 rounded-full flex items-center justify-center">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  ) : step.active ? (
                    <div className="w-7 h-7 bg-banking-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {step.number}
                    </div>
                  ) : (
                    <div className="w-7 h-7 bg-zinc-700 rounded-full flex items-center justify-center text-zinc-400 text-sm font-bold">
                      {step.number}
                    </div>
                  )}
                </div>

                {/* Step Text */}
                <div className="flex-1 min-w-0">
                  <p
                    className={`
                      text-sm font-medium
                      ${step.completed ? 'text-emerald-400 line-through' : 'text-zinc-300'}
                      ${step.active && !step.completed ? 'text-banking-300' : ''}
                    `}
                  >
                    {step.text}
                  </p>

                  {step.active && !step.completed && (
                    <span className="badge-info mt-1.5">
                      Current Step
                    </span>
                  )}

                  {step.completed && (
                    <span className="badge-success mt-1.5">
                      Completed
                    </span>
                  )}
                </div>

                {step.active && !step.completed && (
                  <Circle className="w-4 h-4 text-banking-500 group-hover:text-banking-400 transition-colors flex-shrink-0 mt-1" />
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="px-5 py-3 bg-zinc-900 border-t border-zinc-800">
        <p className="text-xs text-zinc-500 text-center">
          {completedCount === processGuide.steps.length
            ? 'All steps completed!'
            : 'Click on the current step when completed'
          }
        </p>
      </div>
    </div>
  );
}
