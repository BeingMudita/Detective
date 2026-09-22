import { entityMeta } from "../../lib/presentation";
import type { EntityView, EvidenceView } from "../../lib/types";

interface Props {
  entity: EntityView | null;
  evidence: EvidenceView[];
}

export function InspectorPanel({ entity, evidence }: Props) {
  if (!entity) {
    return (
      <div className="rounded-lg border border-dashed border-border p-3 text-xs text-muted">
        Select an entity on the board to inspect it.
      </div>
    );
  }

  const meta = entityMeta(entity.type);
  const related = evidence.filter((e) => e.related.includes(entity.ext_id));
  const attrs = Object.entries(entity.attributes ?? {});

  return (
    <div className="rounded-lg border border-border bg-bg p-3">
      <div className="flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-md bg-surface-2 text-base">
          {meta.icon}
        </span>
        <div className="min-w-0">
          <div className="truncate font-mono text-sm text-text">{entity.label}</div>
          <div className="font-mono text-[10px] uppercase tracking-wider text-faint">
            {meta.label}
            {entity.via ? ` · ${entity.via}` : ""}
          </div>
        </div>
      </div>

      {attrs.length > 0 && (
        <dl className="mt-2 space-y-0.5">
          {attrs.map(([k, v]) => (
            <div key={k} className="flex justify-between gap-2 font-mono text-[11px]">
              <dt className="text-faint">{k}</dt>
              <dd className="truncate text-muted">{String(v)}</dd>
            </div>
          ))}
        </dl>
      )}

      {related.length > 0 && (
        <div className="mt-2">
          <p className="font-mono text-[10px] uppercase tracking-wider text-faint">
            Related evidence
          </p>
          <div className="mt-1 flex flex-wrap gap-1">
            {related.map((r) => (
              <span key={r.ext_id} className="font-mono text-[10px] text-accent">
                {r.ext_id}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
