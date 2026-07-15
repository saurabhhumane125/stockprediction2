import { useState } from 'react';
import { visionApi } from '@/lib/api/services';export type VisionState = 'IDLE' | 'UPLOADING' | 'PROCESSING' | 'COMPLETED' | 'ERROR';

export interface VisionResult {
  prediction: string;
  confidence: number;
  trace: any;
}

export function useVisionPipeline() {
  const [state, setState] = useState<VisionState>('IDLE');
  const [result, setResult] = useState<VisionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const processImage = async (file: File) => {
    try {
      setState('UPLOADING');
      setError(null);
      setResult(null);

      // Create object URL for preview
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);

      // 1. Upload
      const uploadRes = await visionApi.uploadFile(file);
      
      // 2. Predict
      setState('PROCESSING');
      const predictRes = await visionApi.predictVision({
        filename: uploadRes.filename,
        trace_id: `trace-${Date.now()}`
      });

      setResult({
        prediction: predictRes.prediction,
        confidence: predictRes.confidence,
        trace: predictRes.trace
      });
      setState('COMPLETED');
    } catch (err: any) {
      console.error('Vision Pipeline Error:', err);
      setState('ERROR');
      
      const errMsg = err.response?.data?.detail || err.message || "An unknown error occurred.";
      setError(errMsg);
    }
  };

  const reset = () => {
    setState('IDLE');
    setResult(null);
    setError(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
  };

  return {
    state,
    result,
    error,
    previewUrl,
    processImage,
    reset
  };
}
