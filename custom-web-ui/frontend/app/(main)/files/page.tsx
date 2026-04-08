"use client";

import { useCallback, useEffect, useState } from "react";

type IndexSummary = { id: number; name: string };
type FileEntry = {
  id: string;
  name: string;
  size_bytes: number;
  size: string;
  date_created: string;
};

export default function FilesPage() {
  const [indices, setIndices] = useState<IndexSummary[]>([]);
  const [indexId, setIndexId] = useState<number | null>(null);
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [filter, setFilter] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const loadFiles = useCallback(
    async (id: number, q: string) => {
      const qs = q ? `?q=${encodeURIComponent(q)}` : "";
      const res = await fetch(`/api/index/${id}/files${qs}`, {
        credentials: "include",
        cache: "no-store",
      });
      if (!res.ok) {
        setError(`Failed to list files (${res.status})`);
        return;
      }
      const payload = (await res.json()) as FileEntry[];
      setFiles(payload);
    },
    [],
  );

  useEffect(() => {
    let active = true;
    fetch("/api/index", { credentials: "include", cache: "no-store" })
      .then(async (res) => {
        if (!active) return;
        if (!res.ok) {
          setError(`Failed to load indices (${res.status})`);
          setLoading(false);
          return;
        }
        const payload = (await res.json()) as IndexSummary[];
        if (!active) return;
        setIndices(payload);
        const first = payload[0]?.id ?? null;
        setIndexId(first);
        setLoading(false);
        if (first != null) {
          void loadFiles(first, "");
        }
      })
      .catch(() => {
        if (!active) return;
        setError("Failed to load indices");
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [loadFiles]);

  useEffect(() => {
    if (indexId == null) return;
    void loadFiles(indexId, filter);
  }, [indexId, filter, loadFiles]);

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file || indexId == null) return;
    setError(null);
    setUploading(true);
    const fd = new FormData();
    fd.append("file", file);
    try {
      const res = await fetch(`/api/index/${indexId}/upload`, {
        method: "POST",
        credentials: "include",
        body: fd,
      });
      const data = (await res.json()) as { ok: boolean; error?: string };
      if (!res.ok || !data.ok) {
        setError(data.error ?? `Upload failed (${res.status})`);
        return;
      }
      await loadFiles(indexId, filter);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function onDelete(fileId: string) {
    if (indexId == null) return;
    if (!window.confirm("Remove this file from the index?")) return;
    setError(null);
    const res = await fetch(`/api/index/${indexId}/files/${encodeURIComponent(fileId)}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (!res.ok) {
      setError(`Delete failed (${res.status})`);
      return;
    }
    await loadFiles(indexId, filter);
  }

  return (
    <main className="flex flex-1 flex-col gap-4 px-6 py-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          Files
        </h1>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          Upload and manage the primary file index (Phase 5).
        </p>
      </div>

      {indices.length > 1 ? (
        <label className="flex max-w-md flex-col gap-1 text-sm">
          <span className="text-zinc-600 dark:text-zinc-400">Index</span>
          <select
            value={indexId ?? ""}
            onChange={(e) => setIndexId(Number(e.target.value))}
            className="rounded border border-zinc-300 bg-white px-3 py-2 text-zinc-900 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          >
            {indices.map((idx) => (
              <option key={idx.id} value={idx.id}>
                {idx.name} (id {idx.id})
              </option>
            ))}
          </select>
        </label>
      ) : null}

      <div className="flex flex-wrap items-end gap-4">
        <label className="flex max-w-md flex-1 flex-col gap-1 text-sm">
          <span className="text-zinc-600 dark:text-zinc-400">Filter by name</span>
          <input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Substring…"
            className="rounded border border-zinc-300 bg-white px-3 py-2 text-zinc-900 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          />
        </label>
        <label className="inline-flex cursor-pointer items-center rounded bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200">
          {uploading ? "Uploading…" : "Upload file"}
          <input type="file" className="sr-only" disabled={uploading || indexId == null} onChange={(e) => void onUpload(e)} />
        </label>
      </div>

      {error ? (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      ) : null}

      {loading ? (
        <p className="text-sm text-zinc-500">Loading…</p>
      ) : indexId == null ? (
        <p className="text-sm text-zinc-500">No file index configured.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900">
              <tr>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Size</th>
                <th className="px-4 py-2 font-medium">Added</th>
                <th className="px-4 py-2 font-medium" />
              </tr>
            </thead>
            <tbody>
              {files.map((f) => (
                <tr key={f.id} className="border-b border-zinc-100 dark:border-zinc-800">
                  <td className="px-4 py-2 text-zinc-900 dark:text-zinc-100">{f.name}</td>
                  <td className="px-4 py-2 text-zinc-600 dark:text-zinc-400">{f.size}</td>
                  <td className="px-4 py-2 text-zinc-600 dark:text-zinc-400">{f.date_created}</td>
                  <td className="px-4 py-2 text-right">
                    <button
                      type="button"
                      className="text-red-600 hover:underline dark:text-red-400"
                      onClick={() => void onDelete(f.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {files.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-zinc-500">
                    No files yet. Upload a document to index it.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
