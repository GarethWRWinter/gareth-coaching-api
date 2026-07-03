"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useRef, useEffect, useCallback, Suspense } from "react";
import Link from "next/link";
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

  const [showSessions, setShowSessions] = useState(false);

  return (
    <div className="flex h-[calc(100vh-5rem)] gap-0 md:h-[calc(100vh-3rem)] md:gap-4">
      {/* Sessions Sidebar - hidden on mobile, toggle with button */}
      <div
        className={cn(
          "shrink-0 overflow-y-auto rounded-md border border-vb-border-subtle bg-vb-surface",
          showSessions
            ? "absolute inset-x-4 top-16 z-30 max-h-[60vh] md:static md:inset-auto md:z-auto md:max-h-none md:w-64"
            : "hidden md:block md:w-64"
        )}
      >
        <div className="border-b border-vb-border-subtle p-3">
          <button
            onClick={() => {
              createSession.mutate();
              setShowSessions(false);
            }}
            className="flex w-full items-center justify-center gap-2 rounded-sm bg-vb-forest px-3 py-2 text-sm font-medium text-white hover:bg-vb-forest-soft"
          >
            <Plus className="h-4 w-4" /> New Chat
          </button>
        </div>
        <div className="divide-y divide-vb-border-subtle">
          {sessions?.length === 0 && (
            <p className="px-4 py-6 text-center text-xs text-vb-text-muted">
              Start a conversation with your AI coach
            </p>
          )}
          {sessions?.map((session) => (
            <button
              key={session.id}
              onClick={() => {
                setActiveSessionId(session.id);
                setShowSessions(false);
              }}
              className={cn(
                "flex w-full items-center gap-2 px-4 py-3 text-left text-sm transition-colors",
                session.id === activeSessionId
                  ? "bg-vb-sage-tint text-vb-forest"
                  : "text-vb-text-dim hover:bg-vb-surface-raised hover:text-vb-text"
              )}
            >
              <MessageCircle className="h-4 w-4 shrink-0" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-xs font-medium">
                  {session.title || "Chat"}
                </p>
                <p className="text-[10px] text-vb-text-muted">
                  {session.message_count} messages
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Mobile sessions overlay backdrop */}
      {showSessions && (
        <div
          className="fixed inset-0 z-20 bg-black/40 md:hidden"
          onClick={() => setShowSessions(false)}
        />
      )}

      {/* Chat Area */}
      <div className="flex flex-1 flex-col overflow-hidden rounded-md border border-vb-border-subtle bg-vb-surface">
        {/* Mobile chat header */}
        <div className="flex items-center gap-2 border-b border-vb-border-subtle px-3 py-2 md:hidden">
          <button
            onClick={() => setShowSessions(!showSessions)}
            className="rounded-sm p-1.5 text-vb-text-dim hover:bg-vb-surface-raised hover:text-vb-text"
          >
            <MessageCircle className="h-5 w-5" />
          </button>
          <span className="text-sm font-medium text-vb-text-dim">
            {sessions?.find((s) => s.id === activeSessionId)?.title || "Coach Marco"}
          </span>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-3 sm:p-5">
          {messages.length === 0 && (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <Bot className="mx-auto h-12 w-12 text-vb-forest/50" />
                <h3 className="mt-4 font-display text-lg font-light tracking-[-0.01em] text-vb-text">
                  Coach Marco
                </h3>
                <p className="mt-1 max-w-sm text-sm text-vb-text-dim">
                  Training, racing, head, life — ask me anything. And I
                  remember what you tell me: every conversation sharpens{" "}
                  <Link href="/dashboard/brain" className="text-vb-forest hover:underline">
                    your brain
                  </Link>
                  , and better memory makes a better coach.
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
                      className="rounded-full border border-vb-border px-3 py-1.5 text-xs text-vb-text-dim hover:border-vb-forest hover:text-vb-forest"
                    >
                      {q}
                    </button>
                  ))}
                </div>
                {voiceSupported && (
                  <p className="mt-4 text-xs text-vb-text-muted">
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
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-vb-forest">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}
                <div
                  className={cn(
                    "max-w-[90%] rounded-md px-3 py-2.5 text-sm sm:max-w-[80%] sm:px-4 sm:py-3",
                    msg.role === "user"
                      ? "bg-vb-forest text-white"
                      : "bg-vb-sage-tint text-vb-text"
                  )}
                >
                  {msg.role === "assistant" ? (
                    <div className="prose prose-sm max-w-none prose-headings:text-vb-text prose-strong:text-vb-text prose-em:text-vb-clay prose-em:not-italic prose-li:marker:text-vb-forest prose-a:text-vb-forest">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                      {streaming && i === messages.length - 1 && (
                        <span className="ml-0.5 inline-block h-4 w-1.5 animate-pulse bg-vb-forest" />
                      )}
                    </div>
                  ) : (
                    <p>{msg.content}</p>
                  )}
                </div>
                {msg.role === "user" && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-vb-sunken">
                    <User className="h-4 w-4 text-vb-text" />
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-vb-border-subtle p-4">
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
              className="max-h-32 flex-1 resize-none rounded-sm border border-vb-border bg-vb-surface px-4 py-2.5 text-sm text-vb-text placeholder-vb-text-muted focus:border-vb-forest focus:outline-none"
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
              className="flex h-[42px] w-[42px] shrink-0 items-center justify-center rounded-sm bg-vb-forest text-white hover:bg-vb-forest-soft disabled:opacity-50"
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
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-vb-forest border-t-transparent" />
        </div>
      }
    >
      <CoachPageInner />
    </Suspense>
  );
}
