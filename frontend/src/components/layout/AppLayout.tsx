import { useMutation } from "@tanstack/react-query";
import { NavLink, Outlet } from "react-router-dom";
import { logout } from "../../lib/api/auth";
import { useAuthStore } from "../../store/authStore";
import { Button } from "../ui/Button";
import { Logo } from "../ui/Logo";

const NAV = [
  { label: "Dashboard", to: "/" },
  { label: "Cases", to: "/cases" },
];

const SOON = ["Evidence", "Timeline", "Academy"];

export function AppLayout() {
  const user = useAuthStore((s) => s.user);
  const clear = useAuthStore((s) => s.clear);

  const signOut = useMutation({
    mutationFn: () => logout(),
    onSettled: () => clear(),
  });

  return (
    <div className="flex min-h-full">
      {/* sidebar */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-border bg-surface px-4 py-5 md:flex">
        <div className="px-2">
          <Logo />
        </div>
        <nav className="mt-8 flex flex-col gap-1">
          {NAV.map((item) => (
            <NavLink
              key={item.label}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm ${
                  isActive
                    ? "bg-surface-2 font-medium text-text"
                    : "text-muted hover:bg-surface-2 hover:text-text"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
          {SOON.map((label) => (
            <span
              key={label}
              className="cursor-not-allowed rounded-lg px-3 py-2 text-sm text-faint"
            >
              {label}
              <span className="ml-2 font-mono text-[10px] uppercase tracking-wider">soon</span>
            </span>
          ))}
        </nav>
        <div className="mt-auto rounded-lg border border-border px-3 py-3">
          <p className="truncate text-sm font-medium">{user?.display_name}</p>
          <p className="truncate text-xs text-muted">{user?.email}</p>
          <span className="mt-2 inline-block rounded bg-surface-2 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-accent">
            {user?.role}
          </span>
        </div>
      </aside>

      {/* main */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border px-5 py-3">
          <div className="md:hidden">
            <Logo withWordmark={false} />
          </div>
          <div className="font-mono text-xs uppercase tracking-[0.14em] text-muted">
            Investigation Console
          </div>
          <Button variant="ghost" onClick={() => signOut.mutate()} loading={signOut.isPending}>
            Sign out
          </Button>
        </header>
        <main className="min-w-0 flex-1 px-5 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
