import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import type { VisionState } from "../hooks/useVisionPipeline";

interface ProcessingTimelineProps {
  state: VisionState;
}

export function ProcessingTimeline({ state }: ProcessingTimelineProps) {
  const steps = [
    { id: 'upload', label: 'Uploading Image', activeStates: ['UPLOADING', 'PROCESSING', 'COMPLETED'] },
    { id: 'ocr', label: 'Extracting Data (OCR)', activeStates: ['PROCESSING', 'COMPLETED'] },
    { id: 'features', label: 'Generating Features', activeStates: ['PROCESSING', 'COMPLETED'] },
    { id: 'inference', label: 'Running AI Inference', activeStates: ['COMPLETED'] }
  ];

  const getStepStatus = (stepActiveStates: string[], idx: number) => {
    if (state === 'ERROR') return 'error';
    if (state === 'IDLE') return 'pending';
    
    const isCompleted = stepActiveStates.includes(state) && state !== 'UPLOADING' && (state === 'COMPLETED' || steps[idx+1]?.activeStates.includes(state));
    const isCurrent = stepActiveStates.includes(state) && !isCompleted;
    
    if (isCompleted) return 'completed';
    if (isCurrent) return 'current';
    return 'pending';
  };

  return (
    <div className="space-y-4 my-8 p-6 bg-card rounded-xl border border-border">
      <h4 className="font-semibold text-lg mb-4">Processing Timeline</h4>
      <div className="flex flex-col gap-4">
        {steps.map((step, idx) => {
          const status = getStepStatus(step.activeStates, idx);
          
          return (
            <div key={step.id} className="flex items-center gap-3">
              {status === 'completed' && <CheckCircle2 className="w-5 h-5 text-green-500" />}
              {status === 'current' && <Loader2 className="w-5 h-5 text-primary animate-spin" />}
              {status === 'pending' && <Circle className="w-5 h-5 text-muted-foreground" />}
              {status === 'error' && <Circle className="w-5 h-5 text-red-500" />}
              
              <span className={`text-sm ${status === 'current' ? 'font-medium text-foreground' : 'text-muted-foreground'}`}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
