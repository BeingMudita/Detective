import { Badge } from "../../components/ui/Badge";
import { reliabilityClass } from "../../lib/presentation";
import type { EvidenceView } from "../../lib/types";

interface Props {
  evidence: EvidenceView[];
  disabled: boolean;
  busyExt: string | null;
  onCollect: (extId: string) => void;
}

export function EvidencePanel({ evidence, disabled, busyExt, onCollect }: Props) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <h3 className="font-mono text-[11px] uppercase tracking-[0.14em] text-accent">Evidence</h3>
        <span className="font-mono text-[11px] text-faint">
          {evidence.filter((e) => e.collected).length}/{evidence.length} filed
        </span>
      </div>

      {evidence.length === 0 && (
        <p className="text-xs text-muted">
          No evidence yet. Run a lookup to surface leads.
        </p>
      )}

      {evidence.map((ev) => (
        <div key={ev.ext_id} className="rounded-lg border border-border bg-bg p-3">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="font-mono text-xs text-accent">{ev.ext_id}</span>
            <Badge className={reliabilityClass(ev.reliability)}>{ev.reliability}</Badge>
            <span className="font-mono text-[10px] uppercase tracking-wider text-faint">
              {ev.source}
            </span>
          </div>
          <p className="mt-1.5 text-xs leading-relaxed text-muted">{ev.content}</p>
          <div className="mt-2 flex items-center justify-between">
            <div className="flex flex-wrap gap-1">
              {ev.related.map((r) => (
                <span key={r} className="font-mono text-[10px] text-faint">
                  {r}
                </span>
              ))}
            </div>
            {ev.collected ? (
              <span className="font-mono text-[10px] uppercase tracking-wider text-good">
                ✓ Filed
              </span>
            ) : (
              <button
                onClick={() => onCollect(ev.ext_id)}
                disabled={disabled || busyExt === ev.ext_id}
                className="rounded-md border border-border px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-muted hover:border-accent hover:text-accent disabled:opacity-50"
              >
                {busyExt === ev.ext_id ? "…" : "Collect"}
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
