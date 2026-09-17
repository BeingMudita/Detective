import { motion } from "framer-motion";
import { Card } from "../../components/ui/Card";
import { useAuthStore } from "../../store/authStore";

const STAT_CARDS = [
  { label: "Cases solved", value: "0" },
  { label: "Average score", value: "—" },
  { label: "Evidence found", value: "0" },
  { label: "Current rank", value: "Rookie" },
];

export function DashboardPage() {
  const user = useAuthStore((s) => s.user);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="mx-auto max-w-5xl"
    >
      <p className="font-mono text-xs uppercase tracking-[0.16em] text-accent">
        Welcome back
      </p>
      <h1 className="mt-1 font-serif text-3xl font-medium tracking-tight">
        {user?.display_name}
      </h1>
      <p className="mt-1 text-muted">
        Your investigation desk. Cases arrive in Phase 3 — the foundation is live.
      </p>

      <div className="mt-7 grid grid-cols-2 gap-3 lg:grid-cols-4">
        {STAT_CARDS.map((stat) => (
          <Card key={stat.label} className="p-4">
            <div className="font-serif text-2xl font-medium text-accent">
              {stat.value}
            </div>
            <div className="mt-1 font-mono text-[11px] uppercase tracking-wider text-muted">
              {stat.label}
            </div>
          </Card>
        ))}
      </div>

      <Card className="mt-6 flex flex-col items-center justify-center gap-3 px-6 py-14 text-center">
        <span className="grid h-12 w-12 place-items-center rounded-xl bg-surface-2 text-2xl">
          🗂
        </span>
        <h2 className="font-serif text-xl font-medium">No active investigations</h2>
        <p className="max-w-md text-sm text-muted">
          The case engine goes live in Phase 3. Case&nbsp;#001 — “The Midnight Leak” —
          will be your first assignment: correlate clues, collect evidence, reconstruct
          the timeline, and defend your conclusion.
        </p>
        <span className="mt-1 rounded-full border border-border px-3 py-1 font-mono text-[11px] uppercase tracking-wider text-faint">
          Coming in Phase 3
        </span>
      </Card>
    </motion.div>
  );
}
