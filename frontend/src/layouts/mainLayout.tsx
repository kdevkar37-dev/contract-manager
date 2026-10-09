import { LogOut } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { clearAccessToken } from "../services/apiClient";

function MainLayout() {
  const navigate = useNavigate();

  function handleLogout() {
    clearAccessToken();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="fixed left-0 right-0 top-0 z-50 h-16 border-b border-slate-200 bg-white">
        <div className="flex h-16 items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-sm font-bold text-white">
              CM
            </div>

            <div>
              <h1 className="text-lg font-bold text-slate-900">
                Contract Manager
              </h1>

              <p className="text-xs text-slate-500">
                Contract Intelligence Platform
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden text-right sm:block">
              <p className="text-sm font-medium text-slate-700">Manager</p>

              <p className="text-xs text-slate-500">Contract Management</p>
            </div>

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-200 text-sm font-semibold text-slate-700">
              M
            </div>

            <button
              type="button"
              onClick={handleLogout}
              title="Logout"
              className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
            >
              <LogOut size={17} />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex pt-16">
        <aside className="fixed bottom-0 left-0 top-16 hidden w-64 border-r border-slate-200 bg-white md:block">
          <div className="flex h-full flex-col">
            <div className="border-b border-slate-100 px-5 py-5">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Workspace
              </p>
            </div>

            <nav className="flex flex-1 flex-col gap-1 p-4">
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  isActive
                    ? "flex items-center gap-3 rounded-lg bg-slate-900 px-4 py-3 text-sm font-medium text-white"
                    : "flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }
              >
                <span className="text-base">▦</span>
                <span>Dashboard</span>
              </NavLink>

              <NavLink
                to="/contracts"
                className={({ isActive }) =>
                  isActive
                    ? "flex items-center gap-3 rounded-lg bg-slate-900 px-4 py-3 text-sm font-medium text-white"
                    : "flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }
              >
                <span className="text-base">▤</span>
                <span>Contracts</span>
              </NavLink>
            </nav>

            <div className="border-t border-slate-100 p-4">
              <div className="rounded-lg bg-slate-50 p-4">
                <p className="text-xs font-semibold text-slate-700">
                  Contract Intelligence
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Analyze contracts, identify risks and support better
                  decisions.
                </p>
              </div>
            </div>
          </div>
        </aside>

        <main className="min-h-[calc(100vh-4rem)] w-full p-4 sm:p-6 md:ml-64 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default MainLayout;
