/**
 * useMicrophone hook
 *
 * Captures audio from the microphone using the MediaRecorder API.
 * Features:
 * - Records audio and slices it into 200ms chunks
 * - Encodes chunks as base64 for WebSocket transmission
 * - Handles pause/resume functionality
 * - Calculates recording duration
 * - Visual recording indicator
 */

import { useState, useCallback, useRef, useEffect } from 'react';

interface UseMicrophoneOptions {
  chunkDuration?: number; // Duration of each chunk in milliseconds
  sampleRate?: number;
  onChunk?: (chunkBase64: string) => void;
  onError?: (error: Error) => void;
}

interface RecordingState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  volume: number;
}

interface UseMicrophoneReturn {
  recordingState: RecordingState;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  pauseRecording: () => void;
  resumeRecording: () => void;
  resetRecording: () => void;
}

export function useMicrophone(options: UseMicrophoneOptions = {}): UseMicrophoneReturn {
  const {
    chunkDuration = 200, // 200ms chunks
    sampleRate = 16000,
    onChunk,
    onError,
  } = options;

  const [recordingState, setRecordingState] = useState<RecordingState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    volume: 0,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const chunkIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const durationIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const volumeIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Calculate volume from analyser node
  const calculateVolume = useCallback(() => {
    if (!analyserRef.current) return 0;

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
    return Math.min(100, (average / 128) * 100);
  }, []);

  // Start volume monitoring
  const startVolumeMonitoring = useCallback(() => {
    volumeIntervalRef.current = setInterval(() => {
      const volume = calculateVolume();
      setRecordingState((prev) => ({ ...prev, volume }));
    }, 50);
  }, [calculateVolume]);

  // Stop volume monitoring
  const stopVolumeMonitoring = useCallback(() => {
    if (volumeIntervalRef.current) {
      clearInterval(volumeIntervalRef.current);
      volumeIntervalRef.current = null;
    }
    setRecordingState((prev) => ({ ...prev, volume: 0 }));
  }, []);

  // Convert blob to base64
  const blobToBase64 = useCallback((blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = (reader.result as string).split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }, []);

  // Start recording
  const startRecording = useCallback(async () => {
    try {
      console.log('🎤 Starting microphone recording');

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      streamRef.current = stream;

      // Create audio context for volume monitoring
      const audioContext = new AudioContext({ sampleRate });
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;

      source.connect(analyser);

      // Create MediaRecorder
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 16000,
      });

      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.start(100); // Collect data every 100ms
      mediaRecorderRef.current = mediaRecorder;

      // Start chunk interval
      chunkIntervalRef.current = setInterval(async () => {
        if (chunksRef.current.length > 0 && !recordingState.isPaused) {
          const chunk = new Blob(chunksRef.current, { type: mimeType });
          chunksRef.current = [];

          const base64 = await blobToBase64(chunk);
          console.log(`📤 Sending audio chunk (${chunk.size} bytes)`);
          onChunk?.(base64);
        }
      }, chunkDuration);

      // Start duration timer
      durationIntervalRef.current = setInterval(() => {
        setRecordingState((prev) => ({ ...prev, duration: prev.duration + 1 }));
      }, 1000);

      // Start volume monitoring
      startVolumeMonitoring();

      setRecordingState({
        isRecording: true,
        isPaused: false,
        duration: 0,
        volume: 0,
      });

    } catch (error) {
      console.error('Failed to start recording:', error);
      onError?.(error as Error);
      setRecordingState({
        isRecording: false,
        isPaused: false,
        duration: 0,
        volume: 0,
      });
    }
  }, [chunkDuration, sampleRate, recordingState.isPaused, onChunk, onError, blobToBase64, startVolumeMonitoring]);

  // Stop recording
  const stopRecording = useCallback(() => {
    console.log('🛑 Stopping microphone recording');

    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
    }

    if (chunkIntervalRef.current) {
      clearInterval(chunkIntervalRef.current);
      chunkIntervalRef.current = null;
    }

    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
      durationIntervalRef.current = null;
    }

    stopVolumeMonitoring();

    // Stop all tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
      analyserRef.current = null;
    }

    mediaRecorderRef.current = null;

    setRecordingState({
      isRecording: false,
      isPaused: false,
      duration: 0,
      volume: 0,
    });
  }, [stopVolumeMonitoring]);

  // Pause recording
  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.pause();
      console.log('⏸️ Paused recording');
    }

    setRecordingState((prev) => ({ ...prev, isPaused: true }));
  }, []);

  // Resume recording
  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'paused') {
      mediaRecorderRef.current.resume();
      console.log('▶️ Resumed recording');
    }

    setRecordingState((prev) => ({ ...prev, isPaused: false }));
  }, []);

  // Reset recording
  const resetRecording = useCallback(() => {
    stopRecording();
    chunksRef.current = [];
  }, [stopRecording]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording();
    };
  }, [stopRecording]);

  return {
    recordingState,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    resetRecording,
  };
}
