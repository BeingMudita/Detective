import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

export function ProtectedRoute() {
  const status = useAuthStore((s) => s.status);
  if (status === "guest") return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function GuestOnlyRoute() {
  const status = useAuthStore((s) => s.status);
  if (status === "authenticated") return <Navigate to="/" replace />;
  return <Outlet />;
}
