import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi, type PendingValidation } from '../../api/users';

const CAT_COLOR: Record<string, string> = {
  'CRM Odoo': '#006494', 'Ventes': '#01696f', 'Comptabilité': '#da7101', 'Comptabilite': '#da7101',
};

function LevelDots({ current, target }: { current: number; target: number }) {
  return (
    <div className="flex gap-1">
      {[1,2,3,4,5].map(n => (
        <div key={n} className="w-2.5 h-2.5 rounded-full border" style={{
          background: n <= target ? '#01696f' : n <= current ? '#d4d1ca' : 'transparent',
          borderColor: n <= target ? '#01696f' : '#d4d1ca',
        }} />
      ))}
    </div>
  );
}

export default function ValidationPage() {
  const qc = useQueryClient();
  const { data: pending = [], isLoading } = useQuery({
    queryKey: ['validations', 'pending'],
    queryFn: usersApi.getPendingValidations,
  });
  const { mutate: approve } = useMutation({
    mutationFn: ({ id, level }: { id: string; level: number }) => usersApi.validateCompetence(id, level),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['validations'] }),
  });
  const { mutate: reject } = useMutation({
    mutationFn: (id: string) => usersApi.rejectValidation(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['validations'] }),
  });

  if (isLoading) return <div className="p-8 space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 rounded-xl bg-[#f3f0ec] animate-pulse" />)}</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-[#28251d]">Validations en attente</h1>
        <p className="text-[#7a7974] mt-1">{pending.length} demande{pending.length !== 1 ? 's' : ''} à traiter</p>
      </div>
      {pending.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-12 h-12 rounded-full bg-[#d4dfcc] flex items-center justify-center mb-4">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#437a22" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>
          </div>
          <p className="text-[#28251d] font-medium">Tout est à jour !</p>
          <p className="text-sm text-[#7a7974] mt-1">Aucune demande en attente.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {(pending as PendingValidation[]).map(item => {
            const color = CAT_COLOR[item.competence.category] ?? '#7a7974';
            return (
              <div key={item.id} className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl p-5 flex flex-col sm:flex-row sm:items-center gap-4">
                <div className="flex-1 min-w-0">
                  <span className="text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: `${color}18`, color }}>{item.competence.category}</span>
                  <p className="text-sm font-medium text-[#28251d] mt-1 truncate">{item.competence.name}</p>
                  <p className="text-xs text-[#7a7974]">{item.user.full_name} · {item.user.department}</p>
                </div>
                <div className="flex flex-col gap-1.5 shrink-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-[#7a7974] w-20">Actuel</span>
                    <LevelDots current={item.current_level} target={item.current_level} />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-[#7a7974] w-20">Demandé</span>
                    <LevelDots current={item.current_level} target={item.requested_level} />
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <button onClick={() => reject(item.id)} className="px-4 py-2 text-sm rounded-lg border border-[#dcd9d5] text-[#7a7974] hover:border-[#a12c7b] hover:text-[#a12c7b] transition-colors">Refuser</button>
                  <button onClick={() => approve({ id: item.id, level: item.requested_level })} className="px-4 py-2 text-sm rounded-lg bg-[#01696f] text-white hover:bg-[#0c4e54] transition-colors">Valider</button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}