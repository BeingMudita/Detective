import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Spinner } from "../../components/ui/Spinner";
import { Stars } from "../../components/ui/Stars";
import { getCaseBrief, startCase } from "../../lib/api/cases";
import { entityMeta, reliabilityClass } from "../../lib/presentation";

export function CaseBriefPage() {
  const { code = "" } = useParams();
  const navigate = useNavigate();

  const { data: brief, isLoading, isError } = useQuery({
    queryKey: ["case", code],
    queryFn: () => getCaseBrief(code),
  });

  const start = useMutation({
    mutationFn: () => startCase(code),
    onSuccess: (res) => navigate(`/investigations/${res.investigation_id}`),
  });

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Spinner label="Opening case file" />
      </div>
    );
  }
  if (isError || !brief) {
    return (
      <div className="mx-auto max-w-2xl py-16 text-center">
        <p className="text-bad">Case not found.</p>
        <Link to="/cases" className="mt-4 inline-block text-accent hover:underline">
          Back to cases
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl">
      <Link to="/cases" className="font-mono text-xs text-muted hover:text-text">
        ← All cases
      </Link>

      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mt-4 flex items-center gap-3">
          <span className="font-mono text-sm text-accent">{brief.code}</span>
          <Stars value={brief.difficulty} />
        </div>
        <h1 className="mt-2 font-serif text-4xl font-medium tracking-tight">{brief.title}</h1>
        <p className="mt-1 font-mono text-xs uppercase tracking-wider text-faint">
          {brief.org}
        </p>

        <p className="mt-5 border-l-2 border-accent pl-4 font-serif text-lg italic text-muted">
          {brief.summary}
        </p>

        <div className="mt-6">
          <h3 className="font-mono text-xs uppercase tracking-[0.14em] text-accent">
            Learning objectives
          </h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {brief.learning_objectives.map((o) => (
              <Badge key={o} className="border-border text-muted">
                {o}
              </Badge>
            ))}
          </div>
        </div>

        <h3 className="mt-8 font-mono text-xs uppercase tracking-[0.14em] text-accent">
          Initial evidence package
        </h3>

        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          {brief.initial_evidence_package.entities.map((e) => (
            <Card key={e.ext_id} className="flex items-center gap-3 p-3">
              <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-surface-2 text-base">
                {entityMeta(e.type).icon}
              </span>
              <div className="min-w-0">
                <div className="truncate font-mono text-sm">{e.label}</div>
                <div className="font-mono text-[10px] uppercase tracking-wider text-faint">
                  {entityMeta(e.type).label}
                </div>
              </div>
            </Card>
          ))}
        </div>

        <div className="mt-3 space-y-2">
          {brief.initial_evidence_package.evidence.map((ev) => (
            <Card key={ev.ext_id} className="p-3">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-accent">{ev.ext_id}</span>
                <Badge className={reliabilityClass(ev.reliability)}>{ev.reliability}</Badge>
                <span className="font-mono text-[10px] uppercase tracking-wider text-faint">
                  {ev.source}
                </span>
              </div>
              <p className="mt-1.5 text-sm text-muted">{ev.content}</p>
            </Card>
          ))}
        </div>

        <div className="mt-8 flex items-center gap-4">
          <Button loading={start.isPending} onClick={() => start.mutate()}>
            Start investigation →
          </Button>
          {start.isError && (
            <span className="text-sm text-bad">Couldn’t start. Try again.</span>
          )}
        </div>
      </motion.div>
    </div>
  );
}
