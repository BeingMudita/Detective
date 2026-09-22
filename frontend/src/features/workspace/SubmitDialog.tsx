import { useState } from "react";
import { Button } from "../../components/ui/Button";
import { Modal } from "../../components/ui/Modal";
import { entityMeta, formatVector } from "../../lib/presentation";
import type { EntityView, EvidenceView } from "../../lib/types";

interface Props {
  entities: EntityView[];
  evidence: EvidenceView[];
  attackVectors: string[];
  busy: boolean;
  error: string | null;
  onClose: () => void;
  onSubmit: (actor: string, vector: string, cited: string[], summary: string) => void;
}

export function SubmitDialog({
  entities,
  evidence,
  attackVectors,
  busy,
  error,
  onClose,
  onSubmit,
}: Props) {
  const collected = evidence.filter((e) => e.collected);
  const [actor, setActor] = useState("");
  const [vector, setVector] = useState("");
  const [cited, setCited] = useState<string[]>([]);
  const [summary, setSummary] = useState("");

  const toggle = (ext: string) =>
    setCited((c) => (c.includes(ext) ? c.filter((x) => x !== ext) : [...c, ext]));

  const canSubmit = actor && vector;

  return (
    <Modal title="Submit your conclusion" onClose={onClose} width="max-w-xl">
      <div className="flex flex-col gap-5">
        <div>
          <label className="field-label">Who was responsible?</label>
          <select
            className="input"
            value={actor}
            onChange={(e) => setActor(e.target.value)}
          >
            <option value="">Select an entity you discovered…</option>
            {entities.map((e) => (
              <option key={e.ext_id} value={e.ext_id}>
                {entityMeta(e.type).icon} {e.label} ({e.type})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="field-label">What was the attack vector?</label>
          <select
            className="input"
            value={vector}
            onChange={(e) => setVector(e.target.value)}
          >
            <option value="">Select a vector…</option>
            {attackVectors.map((v) => (
              <option key={v} value={v}>
                {formatVector(v)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="field-label">
            Supporting evidence ({cited.length} cited)
          </label>
          {collected.length === 0 ? (
            <p className="text-xs text-muted">
              You haven’t filed any evidence yet. You can still submit, but a defensible case cites
              evidence.
            </p>
          ) : (
            <div className="max-h-40 space-y-1 overflow-y-auto">
              {collected.map((ev) => (
                <label
                  key={ev.ext_id}
                  className="flex cursor-pointer items-start gap-2 rounded-md border border-border p-2 text-xs"
                >
                  <input
                    type="checkbox"
                    checked={cited.includes(ev.ext_id)}
                    onChange={() => toggle(ev.ext_id)}
                    className="mt-0.5 accent-[var(--accent)]"
                  />
                  <span>
                    <span className="font-mono text-accent">{ev.ext_id}</span>{" "}
                    <span className="text-muted">{ev.content}</span>
                  </span>
                </label>
              ))}
            </div>
          )}
        </div>

        <div>
          <label className="field-label">What happened? (optional)</label>
          <textarea
            className="input min-h-[80px] resize-y"
            placeholder="Summarise the sequence of events your evidence supports…"
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
          />
        </div>

        {error && <p className="text-sm text-bad">{error}</p>}

        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>
            Keep investigating
          </Button>
          <Button
            loading={busy}
            disabled={!canSubmit}
            onClick={() => onSubmit(actor, vector, cited, summary)}
          >
            Submit case
          </Button>
        </div>
      </div>
    </Modal>
  );
}
