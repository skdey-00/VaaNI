/**
 * ProcessGuide Component
 *
 * Displays step-by-step checklist for the current banking process:
 * - Numbered steps with checkboxes
 * - Active step is highlighted
 * - Staff can manually tick steps
 * - Progress indicator
 */

import React from 'react';
import { Check, Circle, ListChecks } from 'lucide-react';
import { ProcessGuide as ProcessGuideType, ProcessStep } from '../types';

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
      <div className={`bg-white flex flex-col ${className}`}>
        <div className="px-5 py-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <ListChecks className="w-5 h-5 text-banking-600" />
            <h2 className="text-lg font-semibold text-gray-900">Process Guide</h2>
          </div>
        </div>

        <div className="flex-1 flex items-center justify-center p-6">
          <p className="text-sm text-gray-500 text-center">
            Process guide will appear based on customer inquiry
          </p>
        </div>
      </div>
    );
  }

  const completedCount = processGuide.steps.filter((s) => s.completed).length;
  const progress = (completedCount / processGuide.steps.length) * 100;

  return (
    <div className={`bg-white flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ListChecks className="w-5 h-5 text-banking-600" />
            <h2 className="text-lg font-semibold text-gray-900">{processGuide.name}</h2>
          </div>
          <span className="text-sm font-medium text-banking-600">
            {completedCount}/{processGuide.steps.length}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
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
                w-full text-left p-4 rounded-lg border-2 transition-all group
                ${step.completed
                  ? 'bg-green-50 border-green-300 hover:bg-green-100'
                  : step.active
                    ? 'bg-banking-50 border-banking-400 shadow-sm'
                    : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                }
                ${step.active ? 'cursor-pointer' : 'cursor-default'}
              `}
            >
              <div className="flex items-start gap-3">
                {/* Step Number / Checkbox */}
                <div className="flex-shrink-0">
                  {step.completed ? (
                    <div className="w-7 h-7 bg-green-500 rounded-full flex items-center justify-center">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  ) : step.active ? (
                    <div className="w-7 h-7 bg-banking-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {step.number}
                    </div>
                  ) : (
                    <div className="w-7 h-7 bg-gray-300 rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {step.number}
                    </div>
                  )}
                </div>

                {/* Step Text */}
                <div className="flex-1 min-w-0">
                  <p
                    className={`
                      text-sm font-medium
                      ${step.completed ? 'text-green-800 line-through' : 'text-gray-800'}
                      ${step.active && !step.completed ? 'text-banking-700' : ''}
                    `}
                  >
                    {step.text}
                  </p>

                  {/* Step Status Badge */}
                  {step.active && !step.completed && (
                    <span className="inline-block mt-1.5 text-xs font-medium text-banking-600 bg-banking-100 px-2 py-0.5 rounded">
                      Current Step
                    </span>
                  )}

                  {step.completed && (
                    <span className="inline-block mt-1.5 text-xs font-medium text-green-600 bg-green-100 px-2 py-0.5 rounded">
                      Completed
                    </span>
                  )}
                </div>

                {/* Clickable indicator for active steps */}
                {step.active && !step.completed && (
                  <Circle className="w-4 h-4 text-banking-400 group-hover:text-banking-600 transition-colors flex-shrink-0 mt-1" />
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="px-5 py-3 bg-gray-50 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          {completedCount === processGuide.steps.length
            ? '✅ All steps completed!'
            : `👆 Click on the current step when completed`
          }
        </p>
      </div>
    </div>
  );
}
