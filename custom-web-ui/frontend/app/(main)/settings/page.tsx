"use client";

import { useEffect, useState } from "react";

type SettingsResponse = {
  settings: Record<string, unknown>;
};

export default function SettingsDebugPage() {
  const [data, setData] = useState<SettingsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setError(null);
      const res = await fetch("/api/settings", {
        credentials: "include",
        cache: "no-store",
      });
      if (!res.ok) {
        if (!active) {
          return;
        }
        setError(`Failed to load settings (${res.status})`);
        return;
      }
      const payload = (await res.json()) as SettingsResponse;
      if (!active) {
        return;
      }
      setData(payload);
    }

    void load();
    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="flex flex-1 flex-col gap-4 px-6 py-6">
      <h1 className="text-xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
        Settings (debug)
      </h1>
      {error ? (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      ) : null}
      <pre className="overflow-x-auto rounded-md border border-zinc-200 bg-zinc-50 p-4 text-xs text-zinc-800 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-200">
        {JSON.stringify(data?.settings ?? {}, null, 2)}
      </pre>
    </main>
  );
}
