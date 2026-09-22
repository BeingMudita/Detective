export function Stars({ value, max = 5 }: { value: number; max?: number }) {
  return (
    <span className="font-mono text-accent" aria-label={`Difficulty ${value} of ${max}`}>
      {"★".repeat(Math.max(0, Math.min(value, max)))}
      <span className="text-faint">{"★".repeat(Math.max(0, max - value))}</span>
    </span>
  );
}
