"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useRef, useEffect, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Send, Plus, MessageCircle, Bot, User, Mic } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { chat, goals as goalsApi } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useVoiceChat } from "@/hooks/useVoiceChat";
import { VoiceButton } from "@/components/voice/VoiceButton";
import { VoiceIndicator } from "@/components/voice/VoiceIndicator";

function CoachPageInner() {
  const queryClient = useQueryClient();
  const searchParams = useSearchParams();
  const goalId = searchParams.get("goal_id");

  const isDebrief = searchParams.get("debrief") === "true";

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [goalMessagePrefilled, setGoalMessagePrefilled] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const audioMutedRef = useRef(false);

  // Voice send handler (defined below, used by hook)
  const handleVoiceSend = useCallback(
    async (transcript: string) => {
      if (!transcript.trim() || streaming) return;

      let sessionId = activeSessionId;

      // Reset audio mute — new message, allow audio again
      audioMutedRef.current = false;

      // Create session if needed
      if (!sessionId) {
        const session = await chat.createSession();
        sessionId = session.id;
        setActiveSessionId(session.id);
        queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
      }

      setMessages((prev) => [
        ...prev,
        { role: "user" as const, content: transcript.trim() },
      ]);
      setStreaming(true);

      // Add empty assistant message
      setMessages((prev) => [
        ...prev,
        { role: "assistant" as const, content: "" },
      ]);

      try {
        let assistantContent = "";
        for await (const chunk of chat.sendVoiceMessage(
          sessionId,
          transcript.trim()
        )) {
          if (chunk.type === "text") {
            // Text always streams fully — never interrupted
            assistantContent += chunk.content;
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                role: "assistant",
                content: assistantContent,
              };
              return updated;
            });
          } else if (chunk.type === "audio" && chunk.content) {
            // Only play audio if not muted by interruption
            if (!audioMutedRef.current) {
              playAudioChunk(chunk.content);
            }
          } else if (chunk.type === "plan_updated") {
            // Coach modified the training plan — refresh calendar data
            queryClient.invalidateQueries({ queryKey: ["workouts-week"] });
          }
        }
      } catch {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: "Sorry, I had trouble connecting. Please try again.",
          };
          return updated;
        });
      }

      setStreaming(false);
      queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [activeSessionId, streaming]
  );

  // Voice chat hook
  const {
    isListening,
    isSpeaking,
    isSupported: voiceSupported,
    interimTranscript,
    startListening,
    stopListening,
    playAudioChunk,
    stopAudio,
  } = useVoiceChat({
    onTranscript: handleVoiceSend,
  });

  // Determine voice indicator mode
  const voiceIndicatorMode = isListening
    ? "listening"
    : streaming && voiceMode
      ? "processing"
      : isSpeaking
        ? "speaking"
        : "idle";

  // Fetch goal data if goal_id is in URL
  const { data: goalData } = useQuery({
    queryKey: ["goal-for-coach", goalId],
    queryFn: () => goalsApi.get(goalId!),
    enabled: !!goalId && !goalMessagePrefilled,
  });

  // Pre-fill message when goal data loads
  useEffect(() => {
    if (goalData && !goalMessagePrefilled) {
      const parts: string[] = [];

      if (isDebrief && goalData.assessment_completed_at) {
        // Debrief mode — post-event conversation
        parts.push(`I just completed ${goalData.event_name}.`);

        if (goalData.finish_time_seconds) {
          const h = Math.floor(goalData.finish_time_seconds / 3600);
          const m = Math.floor((goalData.finish_time_seconds % 3600) / 60);
          parts.push(`I finished in ${h}h ${m}m.`);
        }

        if (goalData.overall_satisfaction) {
          parts.push(`I rated my satisfaction ${goalData.overall_satisfaction}/10`);
        }
        if (goalData.perceived_exertion) {
          parts.push(`and effort ${goalData.perceived_exertion}/10.`);
        }

        const ad = goalData.assessment_data as Record<string, unknown> | null;
        if (ad?.went_well) {
          parts.push(`What went well: ${ad.went_well}.`);
        }
        if (ad?.to_improve) {
          parts.push(`What to improve: ${ad.to_improve}.`);
        }

        parts.push("Can you help me debrief this event?");
      } else {
        // Preparation mode
        parts.push(
          `I'd like your help preparing for ${goalData.event_name} on ${goalData.event_date}.`
        );
        parts.push(
          `It's a ${goalData.event_type.replace(/_/g, " ")} (${goalData.priority.replace(/_/g, " ")} priority).`
        );

        if (goalData.route_data) {
          const rd = goalData.route_data;
          const routeParts: string[] = [];
          if (rd.total_distance_km)
            routeParts.push(`${rd.total_distance_km.toFixed(1)}km`);
          if (rd.elevation_gain_m)
            routeParts.push(`${Math.round(rd.elevation_gain_m)}m climbing`);
          if (routeParts.length > 0) {
            parts.push(`The route is ${routeParts.join(" with ")}.`);
          }
        }

        if (goalData.target_duration_minutes) {
          const hours = Math.floor(goalData.target_duration_minutes / 60);
          const mins = goalData.target_duration_minutes % 60;
          const durStr = hours > 0 ? `${hours}h ${mins}m` : `${mins} minutes`;
          parts.push(`My target duration is ${durStr}.`);
        }

        if (goalData.days_until !== null && goalData.days_until > 0) {
          parts.push(`I have ${goalData.days_until} days to prepare.`);
        }

        parts.push("What should my preparation look like?");
      }

      setInput(parts.join(" "));
      setGoalMessagePrefilled(true);

      // Focus the input
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [goalData, goalMessagePrefilled, isDebrief]);

  // Load sessions list
  const { data: sessions } = useQuery({
    queryKey: ["chat-sessions"],
    queryFn: () => chat.getSessions(),
  });

  // Load active session messages
  const { data: sessionData } = useQuery({
    queryKey: ["chat-session", activeSessionId],
    queryFn: () => chat.getSession(activeSessionId!),
    enabled: !!activeSessionId,
  });

  // When session data loads, set messages
  useEffect(() => {
    if (sessionData?.messages) {
      setMessages(
        sessionData.messages.map((m) => ({
          role: m.role,
          content: m.content,
        }))
      );
    }
  }, [sessionData]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Create new session
  const createSession = useMutation({
    mutationFn: () => chat.createSession(),
    onSuccess: (session) => {
      setActiveSessionId(session.id);
      setMessages([]);
      queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
    },
  });

  // Send message with streaming
  const handleSend = async () => {
    if (!input.trim() || streaming) return;

    let sessionId = activeSessionId;

    // Create session if none active
    if (!sessionId) {
      const session = await chat.createSession();
      sessionId = session.id;
      setActiveSessionId(session.id);
      queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
    }

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setStreaming(true);

    // Add empty assistant message
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      let assistantContent = "";
      for await (const chunk of chat.sendMessage(sessionId, userMessage)) {
        if (chunk.type === "text") {
          assistantContent += chunk.content;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              role: "assistant",
              content: assistantContent,
            };
            return updated;
          });
        } else if (chunk.type === "plan_updated") {
          // Coach modified the training plan — refresh calendar data
          queryClient.invalidateQueries({ queryKey: ["workouts-week"] });
        }
      }
    } catch (error) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content:
            "Sorry, I had trouble connecting. Please try again.",
        };
        return updated;
      });
    }

    setStreaming(false);
    queryClient.invalidateQueries({ queryKey: ["chat-sessions"] });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-[calc(100vh-3rem)] gap-4">
      {/* Sessions Sidebar */}
      <div className="w-64 shrink-0 overflow-y-auto rounded-xl border border-slate-800 bg-slate-800/50">
        <div className="border-b border-slate-700 p-3">
          <button
            onClick={() => createSession.mutate()}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-500"
          >
            <Plus className="h-4 w-4" /> New Chat
          </button>
        </div>
        <div className="divide-y divide-slate-800">
          {sessions?.length === 0 && (
            <p className="px-4 py-6 text-center text-xs text-slate-500">
              Start a conversation with your AI coach
            </p>
          )}
          {sessions?.map((session) => (
            <button
              key={session.id}
              onClick={() => setActiveSessionId(session.id)}
              className={cn(
                "flex w-full items-center gap-2 px-4 py-3 text-left text-sm transition-colors",
                session.id === activeSessionId
                  ? "bg-blue-600/10 text-blue-400"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
              )}
            >
              <MessageCircle className="h-4 w-4 shrink-0" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium">
                  {session.title || "Chat"}
                </p>
                <p className="text-[10px] text-slate-500">
                  {session.message_count} messages
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex flex-1 flex-col rounded-xl border border-slate-800 bg-slate-800/50">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-5">
          {messages.length === 0 && (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <Bot className="mx-auto h-12 w-12 text-blue-400/50" />
                <h3 className="mt-4 text-lg font-medium text-white">
                  Coach Marco
                </h3>
                <p className="mt-1 max-w-sm text-sm text-slate-400">
                  Your personal cycling performance partner. Ask me about
                  training, race preparation, mental performance, or how to
                  balance cycling with the rest of your life.
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {[
                    "How is my fitness trending?",
                    "What should I do today?",
                    "Am I training too hard?",
                    "Help me prepare for my next race",
                  ].map((q) => (
                    <button
                      key={q}
                      onClick={() => {
                        setInput(q);
                        inputRef.current?.focus();
                      }}
                      className="rounded-full border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:border-blue-500 hover:text-blue-400"
                    >
                      {q}
                    </button>
                  ))}
                </div>
                {voiceSupported && (
                  <p className="mt-4 text-xs text-slate-500">
                    <Mic className="mr-1 inline h-3 w-3" />
                    Tap the mic to talk with your coach
                  </p>
                )}
              </div>
            </div>
          )}

          <div className="space-y-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  "flex gap-3",
                  msg.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                {msg.role === "assistant" && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-600">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}
                <div
                  className={cn(
                    "max-w-[80%] rounded-2xl px-4 py-3 text-sm",
                    msg.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-slate-700/50 text-slate-200"
                  )}
                >
                  {msg.role === "assistant" ? (
                    <div className="prose prose-invert prose-sm max-w-none prose-headings:text-blue-300 prose-strong:text-white prose-em:text-slate-300 prose-li:marker:text-blue-400">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                      {streaming && i === messages.length - 1 && (
                        <span className="ml-0.5 inline-block h-4 w-1.5 animate-pulse bg-blue-400" />
                      )}
                    </div>
                  ) : (
                    <p>{msg.content}</p>
                  )}
                </div>
                {msg.role === "user" && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-600">
                    <User className="h-4 w-4 text-white" />
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-slate-700 p-4">
          {/* Voice indicator — shown during voice interactions */}
          {voiceMode && voiceIndicatorMode !== "idle" && (
            <VoiceIndicator
              mode={voiceIndicatorMode}
              interimTranscript={interimTranscript}
            />
          )}

          <div className="flex items-end gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask your coach anything..."
              rows={1}
              className="max-h-32 flex-1 resize-none rounded-xl border border-slate-600 bg-slate-700 px-4 py-2.5 text-sm text-white placeholder-slate-400 focus:border-blue-500 focus:outline-none"
              style={{
                height: "auto",
                minHeight: "42px",
              }}
              onInput={(e) => {
                const el = e.target as HTMLTextAreaElement;
                el.style.height = "auto";
                el.style.height = Math.min(el.scrollHeight, 128) + "px";
              }}
            />

            {/* Voice button */}
            <VoiceButton
              isListening={isListening}
              isSpeaking={isSpeaking}
              isSupported={voiceSupported}
              isProcessing={streaming}
              onToggle={() => {
                if (isListening) {
                  stopListening();
                } else if (isSpeaking) {
                  // Interrupt coach: stop audio, mute future chunks, start listening
                  stopAudio();
                  audioMutedRef.current = true;
                  setVoiceMode(true);
                  startListening();
                } else {
                  setVoiceMode(true);
                  startListening();
                }
              }}
            />

            {/* Send button */}
            <button
              onClick={handleSend}
              disabled={!input.trim() || streaming}
              className="flex h-[42px] w-[42px] shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CoachPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-[calc(100vh-3rem)] items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
        </div>
      }
    >
      <CoachPageInner />
    </Suspense>
  );
}
