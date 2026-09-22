import { Route, Routes } from "react-router-dom";
import { AppLayout } from "../components/layout/AppLayout";
import { CaseBriefPage } from "../features/cases/CaseBriefPage";
import { CasesPage } from "../features/cases/CasesPage";
import { LoginPage } from "../features/auth/LoginPage";
import { RegisterPage } from "../features/auth/RegisterPage";
import { DashboardPage } from "../features/dashboard/DashboardPage";
import { WorkspacePage } from "../features/workspace/WorkspacePage";
import { NotFound } from "../pages/NotFound";
import { GuestOnlyRoute, ProtectedRoute } from "../routes/ProtectedRoute";

export function AppRouter() {
  return (
    <Routes>
      <Route element={<GuestOnlyRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        {/* app shell (sidebar) */}
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/cases" element={<CasesPage />} />
          <Route path="/cases/:code" element={<CaseBriefPage />} />
        </Route>
        {/* full-screen investigation workspace */}
        <Route path="/investigations/:id" element={<WorkspacePage />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
