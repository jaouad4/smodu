import { useAuth } from "../../hooks/useAuth";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[#28251d]">
          Bonjour, {user?.first_name} 👋
        </h1>
        <p className="mt-1 text-sm text-[#7a7974]">
          Rôle : <span className="font-medium text-[#01696f]">{user?.role}</span>
        </p>
      </div>

      {/* Placeholder KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Onboarding", value: "—", sub: "En cours" },
          { label: "Cours", value: "—", sub: "Inscrits" },
          { label: "Quiz", value: "—", sub: "Tentatives" },
          { label: "Compétences", value: "—", sub: "Validées" },
        ].map((kpi) => (
          <div
            key={kpi.label}
            className="rounded-xl border border-[#dcd9d5] bg-white p-5 shadow-sm"
          >
            <p className="text-xs font-medium text-[#7a7974] uppercase tracking-wide">{kpi.label}</p>
            <p className="mt-2 text-3xl font-semibold text-[#28251d]">{kpi.value}</p>
            <p className="mt-1 text-xs text-[#bab9b4]">{kpi.sub}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
