import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const NAV_ITEMS = [
  { label: "Dashboard", to: "/dashboard", icon: "⬛" },
  // { label: "Onboarding", to: "/onboarding", icon: "🚀" },
  // { label: "Formation", to: "/formation", icon: "📚" },
  // { label: "Évaluations", to: "/evaluations", icon: "📝" },
  // { label: "Compétences", to: "/competences", icon: "🎯" },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-[#f7f6f2] font-sans">
      {/* ── Sidebar ────────────────────────────────────────────── */}
      <aside className="w-60 shrink-0 flex flex-col border-r border-[#dcd9d5] bg-[#f9f8f5]">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-[#dcd9d5]">
          <span className="text-[#01696f] font-bold text-xl tracking-tight">SMODU</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                  isActive
                    ? "bg-[#cedcd8] text-[#0c4e54] font-medium"
                    : "text-[#7a7974] hover:bg-[#f3f0ec] hover:text-[#28251d]",
                ].join(" ")
              }
            >
              <span className="w-5 text-center">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Utilisateur connecté */}
        <div className="border-t border-[#dcd9d5] p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-full bg-[#cedcd8] flex items-center justify-center text-[#01696f] font-semibold text-sm">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-[#28251d] truncate">{user?.full_name}</p>
              <p className="text-xs text-[#7a7974] truncate">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full text-left text-xs text-[#7a7974] hover:text-[#a12c7b] transition-colors px-1"
          >
            Déconnexion
          </button>
        </div>
      </aside>

      {/* ── Contenu principal ───────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
