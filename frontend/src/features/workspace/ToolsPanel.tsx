import { FormEvent, useEffect, useState } from "react";
import { Button } from "../../components/ui/Button";
import { toolLabel } from "../../lib/presentation";

interface Props {
  tools: string[];
  selectedLabel: string | null;
  disabled: boolean;
  busy: boolean;
  onRun: (tool: string, query: string) => void;
}

export function ToolsPanel({ tools, selectedLabel, disabled, busy, onRun }: Props) {
  const [tool, setTool] = useState(tools[0] ?? "search");
  const [query, setQuery] = useState("");

  useEffect(() => {
    if (selectedLabel) setQuery(selectedLabel);
  }, [selectedLabel]);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) onRun(tool, query.trim());
  };

  return (
    <div className="flex h-full flex-col gap-4 overflow-y-auto p-4">
      <div>
        <h3 className="font-mono text-[11px] uppercase tracking-[0.14em] text-accent">
          OSINT tools
        </h3>
        <p className="mt-1 text-xs text-muted">
          Investigate a lead you’ve already surfaced. Click an entity to auto-fill it.
        </p>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {tools.map((t) => (
          <button
            key={t}
            onClick={() => setTool(t)}
            disabled={disabled}
            className={`rounded-md border px-2 py-1 font-mono text-[11px] transition-colors ${
              tool === t
                ? "border-accent bg-surface-2 text-text"
                : "border-border text-muted hover:border-border-strong"
            }`}
          >
            {toolLabel(t)}
          </button>
        ))}
      </div>

      <form onSubmit={submit} className="flex flex-col gap-2">
        <label className="field-label">Query</label>
        <input
          className="input font-mono text-xs"
          placeholder="e.g. nightowl_42"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={disabled}
        />
        <Button type="submit" loading={busy} disabled={disabled || !query.trim()}>
          Run {toolLabel(tool)}
        </Button>
      </form>

      <div className="mt-auto rounded-lg border border-border bg-bg p-3 text-xs text-muted">
        <p className="font-mono text-[10px] uppercase tracking-wider text-faint">Tip</p>
        <p className="mt-1">
          The same handle can appear under different names across sources. Correlate independent
          clues before you accuse anyone.
        </p>
      </div>
    </div>
  );
}
