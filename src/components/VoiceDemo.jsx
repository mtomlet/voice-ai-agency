import { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Phone, PhoneOff, Volume2 } from 'lucide-react';

const OPENAI_API_KEY = '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';

const SYSTEM_PROMPT = `You are an AI voice assistant for a premium voice AI agency called VoiceFlow AI. You're friendly, professional, and conversational - not robotic. Your job is to:

1. Warmly greet callers and introduce yourself as Maya, the AI assistant for VoiceFlow AI
2. Answer questions about voice AI services (inbound handling, outbound sales, appointment setting, lead qualification, customer support)
3. Qualify potential clients by asking about their business, current call volume, and pain points
4. Share that pricing typically ranges from $2,500-$15,000/month depending on complexity
5. Offer to schedule a discovery call with the team
6. Handle objections gracefully and demonstrate the natural flow of AI conversation

Keep responses concise (1-3 sentences typically). Be warm and personable. Use natural conversational patterns. If asked something you don't know, offer to have a human team member follow up.

Remember: You ARE the product demo. Show how natural and helpful voice AI can be. Demonstrate that you can handle interruptions gracefully and maintain context throughout the conversation.`;

const VoiceDemo = () => {
  const [status, setStatus] = useState('idle'); // idle, connecting, connected, speaking, listening
  const [transcript, setTranscript] = useState([]);
  const [error, setError] = useState(null);
  const [audioLevel, setAudioLevel] = useState(0);

  const wsRef = useRef(null);
  const audioContextRef = useRef(null);
  const streamRef = useRef(null);
  const processorRef = useRef(null);
  const playbackQueueRef = useRef([]);
  const isPlayingRef = useRef(false);
  const sourceNodeRef = useRef(null);

  // Convert Float32Array to PCM16
  const floatTo16BitPCM = (float32Array) => {
    const buffer = new ArrayBuffer(float32Array.length * 2);
    const view = new DataView(buffer);
    for (let i = 0; i < float32Array.length; i++) {
      let s = Math.max(-1, Math.min(1, float32Array[i]));
      view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
    }
    return buffer;
  };

  // Convert PCM16 to Float32Array
  const pcm16ToFloat32 = (buffer) => {
    const view = new DataView(buffer);
    const float32Array = new Float32Array(buffer.byteLength / 2);
    for (let i = 0; i < float32Array.length; i++) {
      float32Array[i] = view.getInt16(i * 2, true) / 0x8000;
    }
    return float32Array;
  };

  // Base64 encode
  const arrayBufferToBase64 = (buffer) => {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  };

  // Base64 decode
  const base64ToArrayBuffer = (base64) => {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  };

  // Play audio from queue
  const playNextAudio = useCallback(() => {
    if (isPlayingRef.current || playbackQueueRef.current.length === 0) return;

    isPlayingRef.current = true;
    const audioData = playbackQueueRef.current.shift();

    if (!audioContextRef.current) {
      isPlayingRef.current = false;
      return;
    }

    const float32Data = pcm16ToFloat32(audioData);
    const audioBuffer = audioContextRef.current.createBuffer(1, float32Data.length, 24000);
    audioBuffer.getChannelData(0).set(float32Data);

    const source = audioContextRef.current.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContextRef.current.destination);
    sourceNodeRef.current = source;

    source.onended = () => {
      isPlayingRef.current = false;
      sourceNodeRef.current = null;
      if (playbackQueueRef.current.length > 0) {
        playNextAudio();
      } else {
        setStatus('listening');
      }
    };

    setStatus('speaking');
    source.start();
  }, []);

  // Handle WebSocket messages
  const handleMessage = useCallback((event) => {
    try {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'session.created':
          console.log('Session created');
          // Send session update with our configuration
          wsRef.current?.send(JSON.stringify({
            type: 'session.update',
            session: {
              modalities: ['text', 'audio'],
              instructions: SYSTEM_PROMPT,
              voice: 'alloy',
              input_audio_format: 'pcm16',
              output_audio_format: 'pcm16',
              input_audio_transcription: {
                model: 'whisper-1'
              },
              turn_detection: {
                type: 'server_vad',
                threshold: 0.5,
                prefix_padding_ms: 300,
                silence_duration_ms: 500
              }
            }
          }));
          setStatus('connected');
          setTimeout(() => setStatus('listening'), 500);
          break;

        case 'session.updated':
          console.log('Session updated');
          break;

        case 'conversation.item.created':
          if (data.item?.role === 'assistant' && data.item?.content) {
            const textContent = data.item.content.find(c => c.type === 'text');
            if (textContent?.text) {
              setTranscript(prev => [...prev, { role: 'assistant', text: textContent.text }]);
            }
          }
          break;

        case 'response.audio.delta':
          if (data.delta) {
            const audioData = base64ToArrayBuffer(data.delta);
            playbackQueueRef.current.push(audioData);
            playNextAudio();
          }
          break;

        case 'response.audio_transcript.delta':
          // Real-time transcript of AI response
          break;

        case 'response.audio_transcript.done':
          if (data.transcript) {
            setTranscript(prev => {
              // Update or add the assistant message
              const lastMsg = prev[prev.length - 1];
              if (lastMsg?.role === 'assistant' && !lastMsg.complete) {
                return [...prev.slice(0, -1), { role: 'assistant', text: data.transcript, complete: true }];
              }
              return [...prev, { role: 'assistant', text: data.transcript, complete: true }];
            });
          }
          break;

        case 'input_audio_buffer.speech_started':
          setStatus('listening');
          // Stop any playing audio
          if (sourceNodeRef.current) {
            sourceNodeRef.current.stop();
            sourceNodeRef.current = null;
          }
          playbackQueueRef.current = [];
          isPlayingRef.current = false;
          break;

        case 'input_audio_buffer.speech_stopped':
          setStatus('connected');
          break;

        case 'conversation.item.input_audio_transcription.completed':
          if (data.transcript) {
            setTranscript(prev => [...prev, { role: 'user', text: data.transcript }]);
          }
          break;

        case 'error':
          console.error('WebSocket error:', data.error);
          setError(data.error?.message || 'An error occurred');
          break;

        default:
          // console.log('Unhandled message type:', data.type);
          break;
      }
    } catch (err) {
      console.error('Error parsing message:', err);
    }
  }, [playNextAudio]);

  // Start the demo
  const startDemo = async () => {
    setError(null);
    setTranscript([]);
    setStatus('connecting');

    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Create audio context
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });

      // Connect WebSocket
      const ws = new WebSocket(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17',
        [
          'realtime',
          `openai-insecure-api-key.${OPENAI_API_KEY}`,
          'openai-beta.realtime-v1'
        ]
      );

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onmessage = handleMessage;

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        setError('Failed to connect. Please try again.');
        setStatus('idle');
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
        if (status !== 'idle') {
          setStatus('idle');
        }
      };

      wsRef.current = ws;

      // Set up audio processing for microphone input
      const source = audioContextRef.current.createMediaStreamSource(stream);
      const processor = audioContextRef.current.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      processor.onaudioprocess = (e) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);

          // Calculate audio level for visualization
          let sum = 0;
          for (let i = 0; i < inputData.length; i++) {
            sum += inputData[i] * inputData[i];
          }
          const rms = Math.sqrt(sum / inputData.length);
          setAudioLevel(Math.min(1, rms * 10));

          // Resample from audioContext sample rate to 24000 if needed
          const targetSampleRate = 24000;
          const sourceSampleRate = audioContextRef.current.sampleRate;

          let resampledData;
          if (sourceSampleRate !== targetSampleRate) {
            const ratio = sourceSampleRate / targetSampleRate;
            const newLength = Math.round(inputData.length / ratio);
            resampledData = new Float32Array(newLength);
            for (let i = 0; i < newLength; i++) {
              const srcIndex = i * ratio;
              const srcIndexFloor = Math.floor(srcIndex);
              const srcIndexCeil = Math.min(srcIndexFloor + 1, inputData.length - 1);
              const t = srcIndex - srcIndexFloor;
              resampledData[i] = inputData[srcIndexFloor] * (1 - t) + inputData[srcIndexCeil] * t;
            }
          } else {
            resampledData = inputData;
          }

          const pcmData = floatTo16BitPCM(resampledData);
          const base64Audio = arrayBufferToBase64(pcmData);

          wsRef.current.send(JSON.stringify({
            type: 'input_audio_buffer.append',
            audio: base64Audio
          }));
        }
      };

      source.connect(processor);
      processor.connect(audioContextRef.current.destination);

    } catch (err) {
      console.error('Error starting demo:', err);
      if (err.name === 'NotAllowedError') {
        setError('Microphone permission denied. Please allow microphone access to use the demo.');
      } else {
        setError('Failed to start demo. Please check your microphone and try again.');
      }
      setStatus('idle');
    }
  };

  // Stop the demo
  const stopDemo = useCallback(() => {
    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Stop audio processing
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    // Stop microphone stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Stop any playing audio
    if (sourceNodeRef.current) {
      sourceNodeRef.current.stop();
      sourceNodeRef.current = null;
    }

    // Clear playback queue
    playbackQueueRef.current = [];
    isPlayingRef.current = false;

    setStatus('idle');
    setAudioLevel(0);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopDemo();
    };
  }, [stopDemo]);

  const getStatusText = () => {
    switch (status) {
      case 'connecting': return 'Connecting...';
      case 'connected': return 'Connected';
      case 'speaking': return 'AI Speaking...';
      case 'listening': return 'Listening...';
      default: return 'Ready to Demo';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'connecting': return 'bg-yellow-500';
      case 'connected': return 'bg-gold';
      case 'speaking': return 'bg-gold animate-pulse';
      case 'listening': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <section id="demo" className="section-padding bg-noir-800 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-noir-900 via-noir-800 to-noir-900" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gold/5 rounded-full blur-3xl" />

      <div className="max-w-4xl mx-auto relative z-10">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <span className="text-gold/80 text-sm tracking-ultra uppercase">Experience It Live</span>
          <h2 className="font-serif text-3xl md:text-5xl font-bold text-cream mt-4 mb-4">
            Talk to Our <span className="text-gradient-gold">AI Assistant</span>
          </h2>
          <p className="text-cream/60 max-w-xl mx-auto">
            Experience the power of conversational AI firsthand. Click below to start a real conversation
            with our demo agent, Maya.
          </p>
        </motion.div>

        {/* Demo Card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="glass-card rounded-3xl p-8 md:p-12 border border-gold/10"
        >
          {/* Status Indicator */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <span className={`w-3 h-3 rounded-full ${getStatusColor()}`} />
            <span className="text-cream/70 text-sm">{getStatusText()}</span>
          </div>

          {/* Main Demo Button */}
          <div className="flex justify-center mb-8">
            <AnimatePresence mode="wait">
              {status === 'idle' ? (
                <motion.button
                  key="start"
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={startDemo}
                  className="relative w-32 h-32 md:w-40 md:h-40 rounded-full bg-gradient-to-br from-gold to-gold-dark
                           flex items-center justify-center shadow-lg shadow-gold/20
                           hover:shadow-xl hover:shadow-gold/30 transition-shadow duration-300"
                >
                  {/* Pulsing ring */}
                  <span className="absolute inset-0 rounded-full border-2 border-gold/50 animate-ping" />
                  <span className="absolute inset-2 rounded-full border border-gold/30" />
                  <div className="flex flex-col items-center gap-2">
                    <Phone className="w-8 h-8 md:w-10 md:h-10 text-noir-900" />
                    <span className="text-noir-900 font-semibold text-sm">Start Demo</span>
                  </div>
                </motion.button>
              ) : (
                <motion.div
                  key="active"
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.9, opacity: 0 }}
                  className="relative"
                >
                  {/* Audio Visualization Circle */}
                  <div className="relative w-32 h-32 md:w-40 md:h-40 rounded-full bg-noir-700 border border-gold/30
                                flex items-center justify-center">
                    {/* Waveform bars */}
                    {status === 'speaking' && (
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <motion.div
                            key={i}
                            animate={{
                              scaleY: [0.3, 1, 0.3],
                            }}
                            transition={{
                              duration: 0.5,
                              repeat: Infinity,
                              delay: i * 0.1,
                            }}
                            className="w-2 h-8 bg-gold rounded-full origin-center"
                          />
                        ))}
                      </div>
                    )}
                    {status === 'listening' && (
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <motion.div
                            key={i}
                            animate={{
                              scaleY: 0.3 + audioLevel * 0.7,
                            }}
                            transition={{
                              duration: 0.05,
                            }}
                            style={{
                              animationDelay: `${i * 50}ms`,
                            }}
                            className="w-2 h-8 bg-green-400 rounded-full origin-center"
                          />
                        ))}
                      </div>
                    )}
                    {(status === 'connecting' || status === 'connected') && (
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <div
                            key={i}
                            className="w-2 h-2 bg-gold/50 rounded-full"
                          />
                        ))}
                      </div>
                    )}

                    {/* Status icon overlay */}
                    <div className="absolute bottom-2 right-2">
                      {status === 'speaking' && <Volume2 className="w-5 h-5 text-gold" />}
                      {status === 'listening' && <Mic className="w-5 h-5 text-green-400" />}
                    </div>
                  </div>

                  {/* End Call Button */}
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={stopDemo}
                    className="absolute -bottom-4 left-1/2 -translate-x-1/2 w-14 h-14 rounded-full
                             bg-red-500 hover:bg-red-600 flex items-center justify-center
                             shadow-lg transition-colors duration-200"
                  >
                    <PhoneOff className="w-6 h-6 text-white" />
                  </motion.button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-center"
              >
                <p className="text-red-400 text-sm">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Transcript Area */}
          <div className="mt-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-cream/80 text-sm font-medium">Conversation Transcript</h3>
              {transcript.length > 0 && (
                <button
                  onClick={() => setTranscript([])}
                  className="text-cream/40 text-xs hover:text-cream/60 transition-colors"
                >
                  Clear
                </button>
              )}
            </div>
            <div className="h-48 md:h-64 overflow-y-auto custom-scrollbar bg-noir-900/50 rounded-xl p-4 border border-white/5">
              {transcript.length === 0 ? (
                <div className="h-full flex items-center justify-center">
                  <p className="text-cream/30 text-sm text-center">
                    {status === 'idle'
                      ? 'Click the button above to start a conversation'
                      : 'Waiting for conversation...'}
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {transcript.map((msg, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] px-4 py-2 rounded-2xl ${
                          msg.role === 'user'
                            ? 'bg-gold/20 text-cream rounded-br-md'
                            : 'bg-noir-700 text-cream/90 rounded-bl-md'
                        }`}
                      >
                        <span className="text-xs text-cream/40 block mb-1">
                          {msg.role === 'user' ? 'You' : 'Maya (AI)'}
                        </span>
                        <p className="text-sm">{msg.text}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Tips */}
          <div className="mt-6 text-center">
            <p className="text-cream/40 text-xs">
              Tip: Ask about our services, pricing, or request to schedule a discovery call
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default VoiceDemo;
