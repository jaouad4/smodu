import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { usersApi } from '../../api/users';

const ROLES = ['ADMIN','HR','MANAGER','TRAINER','ODOO_REF','LEARNER'] as const;
const ROLE_LABELS: Record<string,string> = { ADMIN:'Admin', HR:'RH', MANAGER:'Manager', TRAINER:'Formateur', ODOO_REF:'Référent Odoo', LEARNER:'Apprenant' };
const ROLE_COLORS: Record<string,string> = { ADMIN:'#a12c7b', HR:'#006494', MANAGER:'#01696f', TRAINER:'#da7101', ODOO_REF:'#7a39bb', LEARNER:'#7a7974' };

export default function AdminUsersPage() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');

  const { data: users = [], isLoading } = useQuery({ queryKey: ['admin','users'], queryFn: usersApi.getUsers });
  const { mutate: updateRole } = useMutation({ mutationFn: ({ id, role }: { id:string; role:string }) => usersApi.updateUserRole(id, role), onSuccess: () => qc.invalidateQueries({ queryKey: ['admin','users'] }) });
  const { mutate: deactivate } = useMutation({ mutationFn: (id: string) => usersApi.deactivateUser(id), onSuccess: () => qc.invalidateQueries({ queryKey: ['admin','users'] }) });

  const filtered = (users as any[]).filter(u => {
    const s = search.toLowerCase();
    return (!s || `${u.first_name} ${u.last_name} ${u.email}`.toLowerCase().includes(s)) && (roleFilter === 'ALL' || u.role === roleFilter);
  });

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div><h1 className="text-2xl font-semibold text-[#28251d]">Gestion des utilisateurs</h1><p className="text-[#7a7974] mt-1">{users.length} utilisateurs</p></div>
      <div className="flex flex-col sm:flex-row gap-3">
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Rechercher…" className="flex-1 px-4 py-2.5 bg-[#f9f8f5] border border-[#dcd9d5] rounded-lg text-sm text-[#28251d] placeholder:text-[#bab9b4] focus:outline-none focus:border-[#01696f]" />
        <select value={roleFilter} onChange={e => setRoleFilter(e.target.value)} className="px-4 py-2.5 bg-[#f9f8f5] border border-[#dcd9d5] rounded-lg text-sm focus:outline-none focus:border-[#01696f]">
          <option value="ALL">Tous les rôles</option>
          {ROLES.map(r => <option key={r} value={r}>{ROLE_LABELS[r]}</option>)}
        </select>
      </div>
      {isLoading ? <div className="space-y-2">{[1,2,3].map(i=><div key={i} className="h-14 rounded-xl bg-[#f3f0ec] animate-pulse"/>)}</div> : (
        <div className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-[#dcd9d5] bg-[#f3f0ec]">{['Utilisateur','Département','Rôle','Statut','Actions'].map(h=><th key={h} className="text-left px-4 py-3 text-xs font-medium text-[#7a7974]">{h}</th>)}</tr></thead>
            <tbody>
              {filtered.map((u:any) => {
                const color = ROLE_COLORS[u.role] ?? '#7a7974';
                return (
                  <tr key={u.id} className="border-b border-[#dcd9d5] last:border-0 hover:bg-[#f3f0ec]">
                    <td className="px-4 py-3"><p className="font-medium text-[#28251d]">{u.first_name} {u.last_name}</p><p className="text-xs text-[#7a7974]">{u.email}</p></td>
                    <td className="px-4 py-3 text-[#7a7974]">{u.department || '—'}</td>
                    <td className="px-4 py-3">
                      <select defaultValue={u.role} onChange={e => updateRole({ id: u.id, role: e.target.value })} className="text-xs px-2 py-1 rounded-full font-medium focus:outline-none" style={{ background:`${color}18`, color }}>
                        {ROLES.map(r=><option key={r} value={r} style={{background:'#f9f8f5',color:'#28251d'}}>{ROLE_LABELS[r]}</option>)}
                      </select>
                    </td>
                    <td className="px-4 py-3"><span className="text-xs px-2 py-0.5 rounded-full" style={{ background: u.is_active?'#d4dfcc':'#e6e4df', color: u.is_active?'#437a22':'#7a7974' }}>{u.is_active?'Actif':'Inactif'}</span></td>
                    <td className="px-4 py-3">
                      <div className="flex gap-3">
                        {u.role==='LEARNER' && <button onClick={()=>navigate(`/learners/${u.id}`)} className="text-xs text-[#01696f] hover:underline">Voir fiche</button>}
                        {u.is_active && <button onClick={()=>{ if(confirm(`Désactiver ${u.first_name} ?`)) deactivate(u.id); }} className="text-xs text-[#a12c7b] hover:underline">Désactiver</button>}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}