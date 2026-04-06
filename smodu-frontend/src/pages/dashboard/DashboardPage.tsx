import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import { dashboardApi } from '../../api/dashboard';
import { useNavigate } from 'react-router-dom';

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  ONBOARDING:     { label: 'Onboarding',     color: '#006494' },
  TRAINING:       { label: 'Formation',      color: '#da7101' },
  EVALUATION:     { label: 'Évaluation',     color: '#d19900' },
  CONSOLIDATION:  { label: 'Consolidation',  color: '#437a22' },
  VALIDATED:      { label: 'Validé ✓',       color: '#01696f' },
  NOT_READY:      { label: 'Non prêt',       color: '#a12c7b' },
};

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const isManager = user?.role === 'MANAGER' || user?.role === 'ADMIN' || user?.role === 'HR';

  const { data: learnerData, isLoading: loadingLearner } = useQuery({
    queryKey: ['dashboard', 'learner'],
    queryFn: dashboardApi.getLearnerDashboard,
    enabled: !isManager,
  });

  const { data: managerData, isLoading: loadingManager } = useQuery({
    queryKey: ['dashboard', 'manager'],
    queryFn: dashboardApi.getManagerDashboard,
    enabled: isManager,
  });

  const isLoading = loadingLearner || loadingManager;

  if (isLoading) {
    return (
      <div className="p-8 space-y-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-24 rounded-xl bg-[#f3f0ec] animate-pulse" />
        ))}
      </div>
    );
  }

  // ── VUE APPRENANT ──────────────────────────────────────────────
  if (!isManager && learnerData) {
    const status = STATUS_LABELS[learnerData.project_status] ?? { label: learnerData.project_status, color: '#7a7974' };
    return (
      <div className="p-8 max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-2xl font-semibold text-[#28251d]">
            Bonjour, {user?.first_name} 👋
          </h1>
          <p className="text-[#7a7974] mt-1">Voici votre tableau de bord de progression.</p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[
            { label: 'Complétion globale', value: `${learnerData.global_completion}%`, accent: '#01696f' },
            { label: 'Compétences validées', value: learnerData.validated_skills_count, accent: '#437a22' },
            { label: 'Modules actifs', value: learnerData.active_modules.length, accent: '#da7101' },
            { label: 'Statut projet', value: status.label, accent: status.color },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl p-4">
              <p className="text-xs text-[#7a7974] mb-1">{kpi.label}</p>
              <p className="text-xl font-semibold" style={{ color: kpi.accent }}>{kpi.value}</p>
            </div>
          ))}
        </div>

        {/* Progression globale */}
        <div className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl p-6">
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-sm font-medium text-[#28251d]">Progression globale</h2>
            <span className="text-sm font-semibold text-[#01696f]">{learnerData.global_completion}%</span>
          </div>
          <div className="h-2 bg-[#e6e4df] rounded-full overflow-hidden">
            <div
              className="h-full bg-[#01696f] rounded-full transition-all duration-700"
              style={{ width: `${learnerData.global_completion}%` }}
            />
          </div>
        </div>

        {/* Modules actifs */}
        {learnerData.active_modules.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-[#28251d] mb-3">Modules en cours</h2>
            <div className="space-y-2">
              {learnerData.active_modules.map(mod => (
                <button
                  key={mod.id}
                  onClick={() => navigate(`/formation/modules/${mod.id}`)}
                  className="w-full flex items-center justify-between bg-[#f9f8f5] border border-[#dcd9d5] rounded-lg px-4 py-3 hover:border-[#01696f] hover:bg-[#f3f0ec] transition-colors text-left"
                >
                  <div>
                    <p className="text-sm font-medium text-[#28251d]">{mod.title}</p>
                    <p className="text-xs text-[#7a7974]">{mod.level}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-[#01696f]">{mod.completion_percentage}%</p>
                    <div className="w-20 h-1.5 bg-[#e6e4df] rounded-full mt-1">
                      <div className="h-full bg-[#01696f] rounded-full" style={{ width: `${mod.completion_percentage}%` }} />
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Prochaines étapes onboarding */}
        {learnerData.next_steps.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-[#28251d] mb-3">Prochaines étapes</h2>
            <div className="space-y-2">
              {learnerData.next_steps.slice(0, 3).map(step => (
                <div key={step.id} className="flex items-center gap-3 bg-[#f9f8f5] border border-[#dcd9d5] rounded-lg px-4 py-3">
                  <div className={`w-2 h-2 rounded-full shrink-0 ${step.is_completed ? 'bg-[#437a22]' : 'bg-[#dcd9d5]'}`} />
                  <p className="text-sm text-[#28251d]">{step.title}</p>
                  {step.is_mandatory && (
                    <span className="ml-auto text-xs bg-[#fdd1a4] text-[#da7101] px-2 py-0.5 rounded-full">Obligatoire</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // ── VUE MANAGER ────────────────────────────────────────────────
  if (isManager && managerData) {
    return (
      <div className="p-8 max-w-5xl mx-auto space-y-8">
        <div>
          <h1 className="text-2xl font-semibold text-[#28251d]">Dashboard Manager</h1>
          <p className="text-[#7a7974] mt-1">Vue d'ensemble de vos apprenants.</p>
        </div>

        {/* KPIs manager */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[
            { label: 'Apprenants actifs',   value: managerData.kpis.active_learners,       accent: '#01696f' },
            { label: 'Taux complétion moy.', value: `${managerData.kpis.avg_completion_rate}%`, accent: '#437a22' },
            { label: 'Validés projet',       value: managerData.kpis.validated_learners,    accent: '#006494' },
            { label: 'En retard',            value: managerData.kpis.delayed_learners,      accent: '#a12c7b' },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl p-4">
              <p className="text-xs text-[#7a7974] mb-1">{kpi.label}</p>
              <p className="text-xl font-semibold" style={{ color: kpi.accent }}>{kpi.value}</p>
            </div>
          ))}
        </div>

        {/* Table apprenants */}
        <div className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-[#dcd9d5]">
            <h2 className="text-sm font-semibold text-[#28251d]">Apprenants</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#dcd9d5] bg-[#f3f0ec]">
                  {['Apprenant', 'Département', 'Complétion', 'Score quiz', 'Statut'].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-xs font-medium text-[#7a7974]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {managerData.learners.map(l => {
                  const st = STATUS_LABELS[l.project_status] ?? { label: l.project_status, color: '#7a7974' };
                  return (
                    <tr key={l.user.id} className="border-b border-[#dcd9d5] last:border-0 hover:bg-[#f3f0ec] transition-colors">
                      <td className="px-4 py-3">
                        <p className="font-medium text-[#28251d]">{l.user.full_name}</p>
                        <p className="text-xs text-[#7a7974]">{l.user.email}</p>
                      </td>
                      <td className="px-4 py-3 text-[#7a7974]">{l.user.department}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-[#e6e4df] rounded-full">
                            <div className="h-full bg-[#01696f] rounded-full" style={{ width: `${l.completion_percentage}%` }} />
                          </div>
                          <span className="text-xs text-[#28251d]">{l.completion_percentage}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-[#28251d]">{l.quiz_avg_score}%</td>
                      <td className="px-4 py-3">
                        <span className="text-xs px-2 py-1 rounded-full" style={{ background: `${st.color}18`, color: st.color }}>
                          {st.label}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
