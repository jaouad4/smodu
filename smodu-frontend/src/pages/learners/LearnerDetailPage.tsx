import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { usersApi } from '../../api/users';

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  ONBOARDING: { label: 'Onboarding', color: '#006494' },
  TRAINING: { label: 'Formation', color: '#da7101' },
  EVALUATION: { label: 'Évaluation', color: '#d19900' },
  VALIDATED: { label: 'Validé ✓', color: '#01696f' },
  NOT_READY: { label: 'Non prêt', color: '#a12c7b' },
};

function Bar({ value }: { value: number }) {
  return <div className="h-1.5 w-full bg-[#e6e4df] rounded-full overflow-hidden"><div className="h-full bg-[#01696f] rounded-full" style={{ width: `${value}%` }} /></div>;
}

export default function LearnerDetailPage() {
  const { learnerId } = useParams<{ learnerId: string }>();
  const navigate = useNavigate();
  const { data, isLoading, isError } = useQuery({
    queryKey: ['learner', learnerId],
    queryFn: () => usersApi.getLearnerDetail(learnerId!),
    enabled: !!learnerId,
  });

  if (isLoading) return <div className="p-8 space-y-4">{[1,2,3,4].map(i => <div key={i} className="h-28 rounded-xl bg-[#f3f0ec] animate-pulse" />)}</div>;
  if (isError || !data) return <div className="p-8 flex flex-col items-center py-20"><p className="text-[#28251d] font-medium">Apprenant introuvable</p><button onClick={() => navigate(-1)} className="mt-4 text-sm text-[#01696f] underline">Retour</button></div>;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div className="flex items-start gap-4">
        <button onClick={() => navigate(-1)} className="mt-1 p-1.5 rounded-lg hover:bg-[#f3f0ec] transition-colors text-[#7a7974]">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 12H5M12 5l-7 7 7 7" /></svg>
        </button>
        <div>
          <h1 className="text-2xl font-semibold text-[#28251d]">{data.user?.full_name}</h1>
          <p className="text-[#7a7974] text-sm mt-0.5">{data.user?.email} · {data.user?.department}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Compétences validées', value: `${data.competences?.validated ?? 0}/${data.competences?.total ?? 0}`, accent: '#01696f' },
          { label: 'Taux validation', value: `${data.competences?.validation_rate ?? 0}%`, accent: '#437a22' },
          { label: 'Modules actifs', value: data.courses?.filter(c => !c.completed_at).length ?? 0, accent: '#da7101' },
          { label: 'Quiz récents', value: data.recent_quiz_attempts?.length ?? 0, accent: '#006494' },
        ].map(kpi => (
          <div key={kpi.label} className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl p-4">
            <p className="text-xs text-[#7a7974] mb-1">{kpi.label}</p>
            <p className="text-xl font-semibold" style={{ color: kpi.accent }}>{kpi.value}</p>
          </div>
        ))}
      </div>

      {data.competences_by_category && Object.keys(data.competences_by_category).length > 0 && (
        <div className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-[#dcd9d5]"><h2 className="text-sm font-semibold text-[#28251d]">Compétences</h2></div>
          <div className="divide-y divide-[#dcd9d5]">
            {Object.entries(data.competences_by_category).map(([cat, d]) => (
              <div key={cat} className="px-6 py-4">
                <div className="flex justify-between mb-2"><span className="text-sm font-medium text-[#28251d]">{cat}</span><span className="text-xs text-[#7a7974]">{d.validated}/{d.total}</span></div>
                <Bar value={d.total > 0 ? (d.validated / d.total) * 100 : 0} />
                <div className="mt-3 space-y-2">
                  {d.items.map(item => (
                    <div key={item.name} className="flex items-center justify-between">
                      <p className="text-xs text-[#7a7974] truncate max-w-xs">{item.name}</p>
                      <div className="flex gap-0.5 shrink-0">
                        {[1,2,3,4,5].map(n => <div key={n} className="w-2 h-2 rounded-full" style={{ background: n <= item.level ? '#01696f' : '#e6e4df' }} />)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.courses && data.courses.length > 0 && (
        <div className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-[#dcd9d5]"><h2 className="text-sm font-semibold text-[#28251d]">Formation</h2></div>
          {data.courses.map(c => (
            <div key={c.id} className="px-6 py-4 border-b border-[#dcd9d5] last:border-0">
              <div className="flex justify-between mb-1.5"><p className="text-sm text-[#28251d]">{c.course_title}</p><span className="text-xs font-semibold text-[#01696f]">{c.progress_percentage}%</span></div>
              <Bar value={c.progress_percentage} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}