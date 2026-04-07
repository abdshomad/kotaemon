"use client";

import { useEffect, useMemo, useState } from "react";

type Conversation = {
  id: string;
  name: string;
  is_public: boolean;
  date_created: string;
  date_updated: string;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type ConversationDetail = Conversation & {
  data_source: {
    messages?: ChatMessage[];
  };
  last_messages: ChatMessage[];
};

export default function HomePage() {
  const [items, setItems] = useState<Conversation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [info, setInfo] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [streaming, setStreaming] = useState(false);

  async function createConversation() {
    const res = await fetch("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    });
    if (!res.ok) {
      setError(`Failed to create conversation (${res.status})`);
      return;
    }
    const created = (await res.json()) as Conversation;
    setItems((prev) => [created, ...prev]);
    setSelectedId(created.id);
    setMessages([]);
  }

  useEffect(() => {
    let active = true;
    fetch("/api/conversations", {
      credentials: "include",
      cache: "no-store",
    })
      .then(async (res) => {
        if (!active) return;
        if (!res.ok) {
          setError(`Failed to load conversations (${res.status})`);
          setLoading(false);
          return;
        }
        const payload = (await res.json()) as Conversation[];
        if (!active) return;
        setItems(payload);
        setSelectedId(payload[0]?.id ?? null);
        setLoading(false);
      })
      .catch(() => {
        if (!active) return;
        setError("Failed to load conversations");
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const selected = useMemo(
    () => items.find((item) => item.id === selectedId) ?? null,
    [items, selectedId],
  );

  useEffect(() => {
    if (!selectedId) {
      setMessages([]);
      return;
    }
    fetch(`/api/conversations/${selectedId}`, {
      credentials: "include",
      cache: "no-store",
    })
      .then(async (res) => {
        if (!res.ok) {
          setError(`Failed to load conversation detail (${res.status})`);
          return;
        }
        const payload = (await res.json()) as ConversationDetail;
        const fromSource = payload.data_source?.messages;
        if (Array.isArray(fromSource)) {
          setMessages(fromSource);
          return;
        }
        setMessages(Array.isArray(payload.last_messages) ? payload.last_messages : []);
      })
      .catch(() => {
        setError("Failed to load conversation detail");
      });
  }, [selectedId]);

  async function ensureConversation(): Promise<string | null> {
    if (selectedId) {
      return selectedId;
    }
    const res = await fetch("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    });
    if (!res.ok) {
      setError(`Failed to create conversation (${res.status})`);
      return null;
    }
    const created = (await res.json()) as Conversation;
    setItems((prev) => [created, ...prev]);
    setSelectedId(created.id);
    return created.id;
  }

  async function sendMessage() {
    const text = input.trim();
    if (!text || streaming) return;
    setError(null);
    setInfo("");
    const convoId = await ensureConversation();
    if (!convoId) return;

    const nextMessages = [...messages, { role: "user" as const, content: text }, { role: "assistant" as const, content: "" }];
    setMessages(nextMessages);
    setInput("");
    setStreaming(true);

    const res = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ conversation_id: convoId, message: text }),
    });
    if (!res.ok || !res.body) {
      setError(`Failed to start stream (${res.status})`);
      setStreaming(false);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() ?? "";
        for (const chunk of chunks) {
          const dataLine = chunk
            .split("\n")
            .find((line) => line.startsWith("data: "));
          if (!dataLine) continue;
          const payload = JSON.parse(dataLine.slice(6)) as {
            type?: string;
            delta?: string;
            content?: string;
          };
          if (payload.type === "token") {
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];
              if (last && last.role === "assistant") {
                last.content += payload.delta ?? "";
              }
              return updated;
            });
          }
          if (payload.type === "info") {
            setInfo(payload.content ?? "");
          }
        }
      }
    } catch {
      setError("Stream interrupted");
    } finally {
      setStreaming(false);
    }
  }

  return (
    <main className="flex min-h-0 flex-1">
      <aside className="w-80 border-r border-zinc-200 p-4 dark:border-zinc-800">
        <div className="mb-3 flex items-center justify-between">
          <h1 className="text-sm font-semibold uppercase tracking-wide text-zinc-600 dark:text-zinc-300">
            Conversations
          </h1>
          <button
            type="button"
            className="rounded bg-zinc-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
            onClick={() => void createConversation()}
          >
            New
          </button>
        </div>
        {error ? (
          <p className="mb-3 text-xs text-red-600 dark:text-red-400" role="alert">
            {error}
          </p>
        ) : null}
        {loading ? (
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading…</p>
        ) : (
          <ul className="space-y-1">
            {items.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  onClick={() => setSelectedId(item.id)}
                  className={`w-full rounded px-3 py-2 text-left text-sm ${
                    selectedId === item.id
                      ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                      : "text-zinc-700 hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-900"
                  }`}
                >
                  {item.name}
                </button>
              </li>
            ))}
            {items.length === 0 ? (
              <li className="text-sm text-zinc-500 dark:text-zinc-400">No conversations yet.</li>
            ) : null}
          </ul>
        )}
      </aside>
      <section className="flex min-h-0 flex-1 flex-col">
        <div className="border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
          <h2 className="text-lg font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            {selected ? selected.name : "Chat"}
          </h2>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Streaming markdown shell (Phase 4 MVP).
          </p>
        </div>
        <div className="flex min-h-0 flex-1">
          <div className="flex min-h-0 flex-1 flex-col">
            <div className="flex-1 space-y-3 overflow-y-auto px-6 py-4">
              {messages.length === 0 ? (
                <p className="text-sm text-zinc-500 dark:text-zinc-400">
                  Create or select a conversation, then send a message.
                </p>
              ) : (
                messages.map((msg, idx) => (
                  <div
                    key={`${msg.role}-${idx}`}
                    className={`max-w-2xl rounded px-3 py-2 text-sm ${
                      msg.role === "user"
                        ? "ml-auto bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900"
                        : "bg-zinc-100 text-zinc-900 dark:bg-zinc-900 dark:text-zinc-100"
                    }`}
                  >
                    {msg.content || (streaming ? "Thinking..." : "")}
                  </div>
                ))
              )}
            </div>
            <div className="border-t border-zinc-200 p-4 dark:border-zinc-800">
              <div className="flex gap-2">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      void sendMessage();
                    }
                  }}
                  placeholder="Ask something..."
                  className="flex-1 rounded border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
                />
                <button
                  type="button"
                  disabled={streaming}
                  onClick={() => void sendMessage()}
                  className="rounded bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
          <aside className="w-80 border-l border-zinc-200 p-4 dark:border-zinc-800">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-zinc-600 dark:text-zinc-300">
              Info
            </h3>
            <p className="mt-2 whitespace-pre-wrap text-sm text-zinc-700 dark:text-zinc-300">
              {info || "No retrieval info yet."}
            </p>
          </aside>
        </div>
      </section>
    </main>
  );
}
