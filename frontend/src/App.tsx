import { AppRouter } from "./app/router";
import { Spinner } from "./components/ui/Spinner";
import { useBootstrap } from "./hooks/useBootstrap";
import { useAuthStore } from "./store/authStore";

export function App() {
  useBootstrap();
  const status = useAuthStore((s) => s.status);

  if (status === "loading") {
    return (
      <div className="flex min-h-full items-center justify-center">
        <Spinner label="Restoring session" />
      </div>
    );
  }

  return <AppRouter />;
}
