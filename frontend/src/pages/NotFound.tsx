import { Link } from "react-router-dom";

export function NotFound() {
  return (
    <div className="flex min-h-full flex-col items-center justify-center gap-4 px-4 text-center">
      <p className="font-mono text-sm uppercase tracking-[0.2em] text-accent">
        Cold trail · 404
      </p>
      <h1 className="font-serif text-4xl font-medium">This lead goes nowhere.</h1>
      <p className="max-w-sm text-muted">
        The page you were investigating doesn’t exist.
      </p>
      <Link
        to="/"
        className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:border-border-strong"
      >
        Back to the console
      </Link>
    </div>
  );
}
