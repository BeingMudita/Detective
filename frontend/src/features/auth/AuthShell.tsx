import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { Card } from "../../components/ui/Card";
import { Logo } from "../../components/ui/Logo";

interface AuthShellProps {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}

export function AuthShell({ title, subtitle, children, footer }: AuthShellProps) {
  return (
    <div className="relative flex min-h-full items-center justify-center overflow-hidden px-4 py-10">
      {/* subtle clue-network backdrop */}
      <svg
        className="pointer-events-none absolute inset-0 h-full w-full opacity-[0.18]"
        viewBox="0 0 1200 800"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden
      >
        <g fill="none" stroke="var(--accent)" strokeWidth="1">
          <line x1="180" y1="160" x2="420" y2="300" />
          <line x1="420" y1="300" x2="300" y2="520" />
          <line x1="420" y1="300" x2="680" y2="220" />
          <line x1="680" y1="220" x2="900" y2="360" />
          <line x1="900" y1="360" x2="1040" y2="200" />
          <line x1="680" y1="220" x2="760" y2="480" />
        </g>
        <g fill="var(--accent)">
          <circle cx="180" cy="160" r="4" />
          <circle cx="420" cy="300" r="6" />
          <circle cx="300" cy="520" r="4" />
          <circle cx="680" cy="220" r="7" />
          <circle cx="900" cy="360" r="5" />
          <circle cx="1040" cy="200" r="4" />
          <circle cx="760" cy="480" r="5" />
        </g>
      </svg>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="relative z-10 w-full max-w-[420px]"
      >
        <div className="mb-7 flex justify-center">
          <Logo size={34} />
        </div>
        <Card className="p-7">
          <h1 className="font-serif text-2xl font-medium tracking-tight">{title}</h1>
          <p className="mt-1.5 text-sm text-muted">{subtitle}</p>
          <div className="mt-6">{children}</div>
        </Card>
        <p className="mt-5 text-center text-sm text-muted">{footer}</p>
      </motion.div>
    </div>
  );
}
