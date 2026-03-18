"use client";

import { useState } from "react";

/* Shape of the action card returned by the backend */
interface ActionCard {
  objective: string;
  steps: string[];
  docs: string[];
  assigned_to: string;
  repo: string;
  original_task: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const MIN_LENGTH = 10;
const MAX_LENGTH = 300;

/* ── Input validation ──────────────────────────────────────────────────────
   Returns an error string if invalid, or null if the input is acceptable.
   - Strips emojis and non-printable unicode before checking
   - Enforces min/max length
   - Rejects inputs that are only numbers or special characters (no real words)
   ───────────────────────────────────────────────────────────────────────── */
function validateTask(raw: string): { clean: string; error: string | null } {
  // Remove emojis and non-standard unicode (keep basic latin, punctuation, spaces)
  const clean = raw
    .replace(/[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu, "")
    .replace(/[^\x20-\x7E\s]/g, "") // keep only printable ASCII + whitespace
    .trim();

  if (clean.length === 0) {
    return { clean, error: "Please describe your task." };
  }

  if (clean.length < MIN_LENGTH) {
    return { clean, error: `Task is too short — please add more detail (min ${MIN_LENGTH} characters).` };
  }

  if (clean.length > MAX_LENGTH) {
    return { clean, error: `Task is too long — please keep it under ${MAX_LENGTH} characters.` };
  }

  // Must contain at least one real word (2+ letters in a row)
  if (!/[a-zA-Z]{2,}/.test(clean)) {
    return { clean, error: "Please describe the task using words, not just symbols or numbers." };
  }

  return { clean, error: null };
}

export default function Home() {
  const [task, setTask] = useState("");
  const [result, setResult] = useState<ActionCard | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleHydrate() {
    const { clean, error: validationError } = validateTask(task);

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/hydrate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: clean }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Something went wrong");
      }

      const data: ActionCard = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  }

  /* Show live character count color feedback */
  const charCount = task.length;
  const charCountColor =
    charCount > MAX_LENGTH ? "text-red-400" :
    charCount > MAX_LENGTH * 0.85 ? "text-yellow-500" :
    "text-text-muted";

  return (
    <main className="flex flex-1 flex-col items-center px-4 py-16 sm:py-24">
      <div className="w-full max-w-2xl">

        {/* Header */}
        <header className="mb-12 animate-fade-up">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-2 h-8 rounded-sm bg-accent" />
            <h1 className="text-3xl sm:text-4xl font-bold font-serif text-text-primary tracking-tight">
              HydraTask
            </h1>
          </div>
          <p className="text-text-secondary text-lg leading-relaxed ml-5">
            Paste a vague task. Get a structured action card with context,
            steps, docs, and the right owner.
          </p>
        </header>

        {/* Input area */}
        <div className="animate-fade-up" style={{ animationDelay: "0.1s" }}>
          <textarea
            value={task}
            onChange={(e) => {
              setTask(e.target.value);
              if (error) setError(""); // clear error as user types
            }}
            placeholder='e.g. "Fix the slow database" or "Dashboard is showing wrong numbers"'
            rows={3}
            className="w-full bg-bg-surface border border-border rounded-lg px-4 py-3
                       text-text-primary placeholder:text-text-muted font-sans text-base
                       resize-none outline-none transition-colors
                       focus:border-accent focus:ring-1 focus:ring-accent/30"
            onKeyDown={(e) => {
              /* Submit on Enter (Shift+Enter for new line) */
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleHydrate();
              }
            }}
          />

          {/* Character count */}
          <div className="flex justify-end mt-1">
            <span className={`text-xs font-mono ${charCountColor}`}>
              {charCount} / {MAX_LENGTH}
            </span>
          </div>

          <button
            onClick={handleHydrate}
            disabled={loading || !task.trim()}
            className="mt-2 w-full py-3 rounded-lg font-sans font-medium text-base
                       transition-all duration-200 cursor-pointer
                       bg-accent text-white
                       hover:brightness-110
                       disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Hydrating...
              </span>
            ) : (
              "Hydrate Task"
            )}
          </button>
        </div>

        {/* Validation / API error */}
        {error && (
          <div className="mt-4 p-4 rounded-lg bg-red-900/20 border border-red-800/40 text-red-300 text-sm animate-fade-up">
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="mt-10 animate-fade-up">
            <ResultCard card={result} />
          </div>
        )}
      </div>
    </main>
  );
}

/* ── ActionCard display ─────────────────────────────────────────────────── */

function ResultCard({ card }: { card: ActionCard }) {
  return (
    <div className="bg-bg-surface border border-border rounded-xl overflow-hidden stagger">

      {/* Objective */}
      <div className="px-6 py-5 border-b border-border">
        <span className="text-xs font-mono uppercase tracking-wider text-accent-text">
          Objective
        </span>
        <h2 className="mt-1 text-xl font-serif font-bold text-text-primary leading-snug">
          {card.objective}
        </h2>
      </div>

      {/* Steps */}
      <div className="px-6 py-5 border-b border-border">
        <span className="text-xs font-mono uppercase tracking-wider text-accent-text">
          Steps
        </span>
        <ol className="mt-3 space-y-3">
          {card.steps.map((step, i) => (
            <li key={i} className="flex gap-3 text-text-primary">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-accent/15 text-accent-text
                             text-xs font-mono flex items-center justify-center mt-0.5">
                {i + 1}
              </span>
              <span className="leading-relaxed">{step}</span>
            </li>
          ))}
        </ol>
      </div>

      {/* Docs + Assignment */}
      <div className="grid sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x divide-border">

        <div className="px-6 py-5">
          <span className="text-xs font-mono uppercase tracking-wider text-accent-text">
            Documentation
          </span>
          <ul className="mt-2 space-y-1.5">
            {card.docs.map((url, i) => (
              <li key={i}>
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-text-secondary hover:text-accent-text transition-colors
                           underline underline-offset-2 decoration-border hover:decoration-accent
                           break-all font-mono"
                >
                  {url}
                </a>
              </li>
            ))}
          </ul>
        </div>

        <div className="px-6 py-5 space-y-4">
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-accent-text">
              Assigned To
            </span>
            <p className="mt-1 text-text-primary font-medium">{card.assigned_to}</p>
          </div>
          <div>
            <span className="text-xs font-mono uppercase tracking-wider text-accent-text">
              Repository
            </span>
            <a
              href={card.repo}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-1 block text-sm text-text-secondary hover:text-accent-text
                       transition-colors font-mono break-all"
            >
              {card.repo}
            </a>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-3 bg-bg-primary/50 border-t border-border">
        <p className="text-xs text-text-muted font-mono">
          <span className="text-text-secondary">Input:</span> &quot;{card.original_task}&quot;
        </p>
      </div>
    </div>
  );
}
