import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Card } from "../../components/ui/Card";
import { Spinner } from "../../components/ui/Spinner";
import { Stars } from "../../components/ui/Stars";
import { listCases } from "../../lib/api/cases";

export function CasesPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["cases"],
    queryFn: listCases,
  });

  return (
    <div className="mx-auto max-w-5xl">
      <p className="font-mono text-xs uppercase tracking-[0.16em] text-accent">Case files</p>
      <h1 className="mt-1 font-serif text-3xl font-medium tracking-tight">Open investigations</h1>
      <p className="mt-1 text-muted">Pick a case and start connecting the clues.</p>

      {isLoading && (
        <div className="mt-16 flex justify-center">
          <Spinner label="Loading cases" />
        </div>
      )}
      {isError && <p className="mt-8 text-bad">Could not load cases. Is the API running?</p>}

      <div className="mt-7 grid gap-4 sm:grid-cols-2">
        {data?.map((c, i) => (
          <motion.div
            key={c.code}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Link to={`/cases/${c.code}`} className="block">
              <Card className="h-full p-5 transition-colors hover:border-border-strong">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-faint">{c.code}</span>
                  <Stars value={c.difficulty} />
                </div>
                <h2 className="mt-2 font-serif text-xl font-medium">{c.title}</h2>
                <p className="mt-1 text-sm text-muted line-clamp-3">{c.summary}</p>
                <div className="mt-4 flex items-center gap-3 font-mono text-[11px] uppercase tracking-wider text-faint">
                  <span>{c.org}</span>
                  <span>·</span>
                  <span>{c.initial_clues} initial clues</span>
                </div>
              </Card>
            </Link>
          </motion.div>
        ))}
      </div>

      {data && data.length === 0 && (
        <p className="mt-8 text-muted">No cases have been published yet.</p>
      )}
    </div>
  );
}
