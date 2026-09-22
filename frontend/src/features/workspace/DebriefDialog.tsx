import { Button } from "../../components/ui/Button";
import { Modal } from "../../components/ui/Modal";
import { formatVector } from "../../lib/presentation";
import type { Debrief } from "../../lib/types";

function Verdict({ ok, label }: { ok: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className={ok ? "text-good" : "text-bad"}>{ok ? "✓" : "✗"}</span>
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function DebriefDialog({
  debrief,
  onClose,
}: {
  debrief: Debrief;
  onClose: () => void;
}) {
  const v = debrief.verdict;
  const solved = v.correct_actor && v.correct_vector;

  return (
    <Modal title="Case debrief" onClose={onClose} width="max-w-lg">
      <div className="flex flex-col gap-5">
        <div
          className={`rounded-xl border p-4 ${
            solved ? "border-good" : "border-border"
          }`}
        >
          <p className="font-serif text-xl font-medium">
            {solved ? "Case solved" : "Case closed"}
          </p>
          <p className="mt-1 text-sm text-muted">{debrief.message}</p>
        </div>

        <div className="space-y-2">
          <Verdict ok={v.correct_actor} label="Correct actor identified" />
          <Verdict ok={v.correct_vector} label="Correct attack vector" />
          <Verdict
            ok={v.required_collected.length === v.required_total && v.required_total > 0}
            label={`Key evidence filed: ${v.required_collected.length} / ${v.required_total}`}
          />
          <Verdict
            ok={v.red_herrings_collected.length === 0}
            label={
              v.red_herrings_collected.length === 0
                ? "No red herrings mistaken for evidence"
                : `Red herrings filed: ${v.red_herrings_collected.join(", ")}`
            }
          />
        </div>

        <div className="rounded-lg border border-border bg-bg p-4">
          <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-accent">
            The solution
          </p>
          <dl className="mt-2 space-y-1 text-sm">
            <div className="flex justify-between gap-2">
              <dt className="text-muted">Responsible</dt>
              <dd className="font-medium">{debrief.solution.actor_label}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-muted">Attack vector</dt>
              <dd className="font-medium">{formatVector(debrief.solution.attack_vector)}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-muted">Key evidence</dt>
              <dd className="font-mono text-xs text-accent">
                {debrief.solution.required_evidence.join(", ")}
              </dd>
            </div>
          </dl>
        </div>

        <p className="text-xs text-faint">{debrief.note}</p>

        <div className="flex justify-end">
          <Button onClick={onClose}>Back to cases</Button>
        </div>
      </div>
    </Modal>
  );
}
