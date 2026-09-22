import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Button } from "../../components/ui/Button";
import { Logo } from "../../components/ui/Logo";
import { Spinner } from "../../components/ui/Spinner";
import { getAttackVectors, getInvestigation } from "../../lib/api/investigations";
import {
  addEdge,
  collectEvidence,
  runLookup,
  submitCase,
} from "../../lib/api/investigations";
import { ApiError } from "../../lib/api/client";
import type { Debrief } from "../../lib/types";
import { DebriefDialog } from "./DebriefDialog";
import { EvidencePanel } from "./EvidencePanel";
import { GraphCanvas } from "./GraphCanvas";
import { InspectorPanel } from "./InspectorPanel";
import { SubmitDialog } from "./SubmitDialog";
import { ToolsPanel } from "./ToolsPanel";

export function WorkspacePage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const stateQuery = useQuery({
    queryKey: ["investigation", id],
    queryFn: () => getInvestigation(id),
  });
  const vectorsQuery = useQuery({
    queryKey: ["attack-vectors"],
    queryFn: getAttackVectors,
    staleTime: Infinity,
  });

  const [selectedExt, setSelectedExt] = useState<string | null>(null);
  const [banner, setBanner] = useState<{ ok: boolean; text: string } | null>(null);
  const [submitOpen, setSubmitOpen] = useState(false);
  const [debrief, setDebrief] = useState<Debrief | null>(null);

  const invalidate = () => qc.invalidateQueries({ queryKey: ["investigation", id] });

  const lookup = useMutation({
    mutationFn: (v: { tool: string; query: string }) => runLookup(id, v.tool, v.query),
    onSuccess: (res) => {
      const extra =
        res.hit && (res.revealed.entities.length || res.revealed.evidence.length)
          ? ` (+${res.revealed.entities.length} entities, +${res.revealed.evidence.length} evidence)`
          : "";
      setBanner({ ok: res.hit, text: res.message + extra });
      invalidate();
    },
  });

  const collect = useMutation({
    mutationFn: (ext: string) => collectEvidence(id, ext),
    onSuccess: invalidate,
  });

  const connect = useMutation({
    mutationFn: (v: { source: string; target: string }) => addEdge(id, v.source, v.target),
    onSuccess: invalidate,
  });

  const submit = useMutation({
    mutationFn: (v: { actor: string; vector: string; cited: string[]; summary: string }) =>
      submitCase(id, v.actor, v.vector, v.cited, v.summary),
    onSuccess: (d) => {
      setDebrief(d);
      setSubmitOpen(false);
      invalidate();
    },
  });

  useEffect(() => {
    if (!banner) return;
    const t = setTimeout(() => setBanner(null), 4500);
    return () => clearTimeout(t);
  }, [banner]);

  const state = stateQuery.data;
  const selectedEntity = useMemo(
    () => state?.entities.find((e) => e.ext_id === selectedExt) ?? null,
    [state, selectedExt],
  );

  if (stateQuery.isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner label="Loading investigation" />
      </div>
    );
  }
  if (stateQuery.isError || !state) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4">
        <p className="text-bad">Could not load this investigation.</p>
        <Link to="/cases" className="text-accent hover:underline">
          Back to cases
        </Link>
      </div>
    );
  }

  const interactive = state.investigation.status === "ACTIVE";
  const submitError = submit.error instanceof ApiError ? submit.error.message : null;

  return (
    <div className="flex h-screen flex-col bg-bg">
      {/* header */}
      <header className="flex items-center gap-4 border-b border-border px-4 py-2.5">
        <Link to="/cases" aria-label="Back to cases">
          <Logo withWordmark={false} />
        </Link>
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-accent">{state.case.code}</span>
            <span className="truncate font-serif text-base font-medium">{state.case.title}</span>
          </div>
          <div className="font-mono text-[10px] uppercase tracking-wider text-faint">
            {state.case.org}
          </div>
        </div>

        <div className="ml-auto hidden items-center gap-4 font-mono text-[11px] text-muted md:flex">
          <Stat label="Entities" value={state.counts.entities_discovered} />
          <Stat label="Filed" value={state.counts.evidence_collected} />
          <Stat label="Links" value={state.counts.relationships_drawn} />
        </div>

        {interactive ? (
          <Button onClick={() => setSubmitOpen(true)}>Submit case</Button>
        ) : (
          <span className="rounded-md border border-border px-3 py-1.5 font-mono text-[11px] uppercase tracking-wider text-good">
            Submitted
          </span>
        )}
      </header>

      {/* reveal banner */}
      <AnimatePresence>
        {banner && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className={`border-b px-4 py-2 text-sm ${
              banner.ok
                ? "border-good bg-surface text-good"
                : "border-border bg-surface text-muted"
            }`}
          >
            {banner.ok ? "🔎 " : ""}
            {banner.text}
          </motion.div>
        )}
      </AnimatePresence>

      {/* body */}
      <div className="flex min-h-0 flex-1">
        <aside className="hidden w-72 shrink-0 border-r border-border bg-surface md:block">
          <ToolsPanel
            tools={state.tools}
            selectedLabel={selectedEntity?.label ?? null}
            disabled={!interactive}
            busy={lookup.isPending}
            onRun={(tool, query) => lookup.mutate({ tool, query })}
          />
        </aside>

        <div className="relative min-w-0 flex-1">
          <GraphCanvas
            entities={state.entities}
            edges={state.edges}
            interactive={interactive}
            onConnectEntities={(source, target) => connect.mutate({ source, target })}
            onSelectEntity={setSelectedExt}
          />
        </div>

        <aside className="hidden w-80 shrink-0 flex-col border-l border-border bg-surface lg:flex">
          <div className="border-b border-border p-4">
            <InspectorPanel entity={selectedEntity} evidence={state.evidence} />
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto p-4">
            <EvidencePanel
              evidence={state.evidence}
              disabled={!interactive}
              busyExt={collect.isPending ? (collect.variables as string) : null}
              onCollect={(ext) => collect.mutate(ext)}
            />
          </div>
        </aside>
      </div>

      {submitOpen && (
        <SubmitDialog
          entities={state.entities}
          evidence={state.evidence}
          attackVectors={vectorsQuery.data?.attack_vectors ?? []}
          busy={submit.isPending}
          error={submitError}
          onClose={() => setSubmitOpen(false)}
          onSubmit={(actor, vector, cited, summary) =>
            submit.mutate({ actor, vector, cited, summary })
          }
        />
      )}

      {debrief && (
        <DebriefDialog debrief={debrief} onClose={() => navigate("/cases")} />
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className="text-text tabular-nums">{value}</span>
      <span className="uppercase tracking-wider text-faint">{label}</span>
    </span>
  );
}
