"use client";

import { useEffect, useMemo, useState } from "react";

type Conversation = {
  id: string;
  name: string;
  is_public: boolean;
  date_created: string;
  date_updated: string;
};

export default function HomePage() {
  const [items, setItems] = useState<Conversation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

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
      <section className="flex flex-1 items-center justify-center px-6 py-16">
        <div className="text-center">
          <h2 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            {selected ? selected.name : "Chat"}
          </h2>
          <p className="mt-2 max-w-md text-zinc-600 dark:text-zinc-400">
            {selected
              ? "Conversation selected. Streaming chat UI arrives in Phase 4."
              : "Create or select a conversation from the sidebar."}
          </p>
        </div>
      </section>
    </main>
  );
}
