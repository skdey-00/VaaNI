/**
 * useAudioPlayer hook
 *
 * Plays base64-encoded TTS audio using the Web Audio API.
 * Features:
 * - Decodes and plays base64 audio data
 * - Animated waveform visualization
 * - Volume control
 * - Playback state management
 */

import { useState, useCallback, useRef, useEffect } from 'react';

interface UseAudioPlayerOptions {
  autoPlay?: boolean;
  onPlayStart?: () => void;
  onPlayEnd?: () => void;
  onError?: (error: Error) => void;
}

interface PlaybackState {
  isPlaying: boolean;
  volume: number;
  currentTime: number;
  duration: number;
}

interface UseAudioPlayerReturn {
  playbackState: PlaybackState;
  play: (audioBase64: string) => Promise<void>;
  stop: () => void;
  setVolume: (volume: number) => void;
  waveformData: number[]; // For visualization
}

export function useAudioPlayer(options: UseAudioPlayerOptions = {}): UseAudioPlayerReturn {
  const {
    autoPlay = true,
    onPlayStart,
    onPlayEnd,
    onError,
  } = options;

  const [playbackState, setPlaybackState] = useState<PlaybackState>({
    isPlaying: false,
    volume: 1.0,
    currentTime: 0,
    duration: 0,
  });

  const [waveformData, setWaveformData] = useState<number[]>([]);

  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceRef = useRef<AudioBufferSourceNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Initialize audio context
  const getAudioContext = useCallback(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 24000,
      });
    }
    return audioContextRef.current;
  }, []);

  // Update waveform visualization
  const updateWaveform = useCallback(() => {
    if (!analyserRef.current) return;

    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserRef.current.getByteFrequencyData(dataArray);

    // Downsample to 32 bars for visualization
    const bars: number[] = [];
    const step = Math.floor(bufferLength / 32);

    for (let i = 0; i < 32; i++) {
      const sum = dataArray.slice(i * step, (i + 1) * step)
        .reduce((acc, val) => acc + val, 0);
      bars.push(sum / step / 255);
    }

    setWaveformData(bars);

    if (playbackState.isPlaying) {
      animationFrameRef.current = requestAnimationFrame(updateWaveform);
    }
  }, [playbackState.isPlaying]);

  // Play base64 audio
  const play = useCallback(async (audioBase64: string) => {
    try {
      console.log('🔊 Playing TTS audio');

      const audioContext = getAudioContext();

      // Stop any currently playing audio
      if (sourceRef.current) {
        try {
          sourceRef.current.stop();
        } catch (e) {
          // Already stopped
        }
      }

      // Decode base64 audio data
      const binaryString = atob(audioBase64);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      const audioBuffer = await audioContext.decodeAudioData(bytes.buffer);

      // Create audio nodes
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;

      const gainNode = audioContext.createGain();
      gainNode.gain.value = playbackState.volume;

      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;

      // Connect nodes: source -> gain -> analyser -> destination
      source.connect(gainNode);
      gainNode.connect(analyser);
      analyser.connect(audioContext.destination);

      sourceRef.current = source;
      gainNodeRef.current = gainNode;

      // Update state
      setPlaybackState((prev) => ({
        ...prev,
        isPlaying: true,
        duration: audioBuffer.duration,
      }));

      onPlayStart?.();

      // Start waveform visualization
      updateWaveform();

      // Handle playback end
      source.onended = () => {
        setPlaybackState((prev) => ({
          ...prev,
          isPlaying: false,
          currentTime: 0,
        }));
        setWaveformData([]);
        onPlayEnd?.();

        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
      };

      // Start playback
      source.start();

    } catch (error) {
      console.error('Failed to play audio:', error);
      onError?.(error as Error);
    }
  }, [getAudioContext, playbackState.volume, onPlayStart, onPlayEnd, onError, updateWaveform]);

  // Stop playback
  const stop = useCallback(() => {
    if (sourceRef.current) {
      try {
        sourceRef.current.stop();
      } catch (e) {
        // Already stopped
      }
      sourceRef.current = null;
    }

    setPlaybackState((prev) => ({
      ...prev,
      isPlaying: false,
      currentTime: 0,
    }));
    setWaveformData([]);

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, []);

  // Set volume
  const setVolume = useCallback((volume: number) => {
    const clampedVolume = Math.max(0, Math.min(1, volume));

    if (gainNodeRef.current) {
      gainNodeRef.current.gain.value = clampedVolume;
    }

    setPlaybackState((prev) => ({ ...prev, volume: clampedVolume }));
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stop();

      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [stop]);

  return {
    playbackState,
    play,
    stop,
    setVolume,
    waveformData,
  };
}
