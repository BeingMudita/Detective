export function Spinner({ label = "Loading" }: { label?: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex flex-col items-center gap-3 text-muted"
    >
      <span
        className="h-6 w-6 animate-spin rounded-full border-2 border-border border-t-accent"
        aria-hidden
      />
      <span className="font-mono text-xs uppercase tracking-[0.14em]">{label}</span>
    </div>
  );
}
