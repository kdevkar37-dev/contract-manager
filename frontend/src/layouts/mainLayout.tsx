import { Link, Outlet } from "react-router-dom";

function MainLayout() {
  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-slate-900 px-6 py-4 text-white">
        <h1 className="text-xl font-bold">Contract Manager</h1>
      </header>

      <div className="flex">
        <aside className="min-h-[calc(100vh-64px)] w-64 bg-white p-4 shadow">
          <nav className="flex flex-col gap-2">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/contracts">Contracts</Link>
          </nav>
        </aside>

        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default MainLayout;