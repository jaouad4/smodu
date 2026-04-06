import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { competencesApi } from '../../api/competences';
import type { UserSkill } from '../../types';

const LEVEL_ORDER = ['DISCOVERY', 'BEGINNER', 'INTERMEDIATE', 'AUTONOMOUS', 'PROJECT_READY'];
const LEVEL_LABELS: Record<string, string> = {
  DISCOVERY:     'Découverte',
  BEGINNER:      'Débutant',
  INTERMEDIATE:  'Intermédiaire',
  AUTONOMOUS:    'Autonome',
  PROJECT_READY: 'Prêt projet',
};
const LEVEL_COLORS: Record<string, string> = {
  DISCOVERY:     '#006494',
  BEGINNER:      '#437a22',
  INTERMEDIATE:  '#da7101',
  AUTONOMOUS:    '#d19900',
  PROJECT_READY: '#01696f',
};

function SkillRow({ skill, onRequest }: { skill: UserSkill; onRequest: (id: number) => void }) {
  const levelIdx = LEVEL_ORDER.indexOf(skill.level);
  const progress = ((levelIdx + 1) / LEVEL_ORDER.length) * 100;
  const color = LEVEL_COLORS[skill.level];

  return (
    <div className="flex items-center gap-4 px-4 py-3 border-b border-[#dcd9d5] last:border-0">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-[#28251d]">{skill.skill.name}</p>
        <p className="text-xs text-[#7a7974]">{skill.skill.domain.name}</p>
      </div>
      <div className="w-32 hidden sm:block">
        <div className="h-1.5 bg-[#e6e4df] rounded-full">
          <div className="h-full rounded-full transition-all" style={{ width: `${progress}%`, background: color }} />
        </div>
      </div>
      <span className="text-xs px-2 py-1 rounded-full shrink-0" style={{ background: `${color}18`, color }}>
        {LEVEL_LABELS[skill.level]}
      </span>
      {skill.is_validated ? (
        <span className="text-xs text-[#437a22] shrink-0">✓ Validé</span>
      ) : (
        <button
          onClick={() => onRequest(skill.skill.id)}
          className="text-xs border border-[#dcd9d5] px-2 py-1 rounded-lg hover:border-[#01696f] hover:text-[#01696f] transition-colors shrink-0"
        >
          Demander validation
        </button>
      )}
    </div>
  );
}

export default function CompetencesPage() {
  const qc = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ['competences', 'matrix'],
    queryFn: competencesApi.getMyMatrix,
  });

  const { mutate: requestValidation } = useMutation({
    mutationFn: competencesApi.requestValidation,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['competences', 'matrix'] }),
  });

  if (isLoading) {
    return (
      <div className="p-8 space-y-2 max-w-3xl mx-auto">
        {[1, 2, 3, 4, 5].map(i => <div key={i} className="h-14 rounded-lg bg-[#f3f0ec] animate-pulse" />)}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-8 text-center">
        <p className="text-[#a12c7b]">Impossible de charger la matrice de compétences.</p>
      </div>
    );
  }

  // Grouper par domaine
  const byDomain = data.skills.reduce<Record<string, UserSkill[]>>((acc, s) => {
    const d = s.skill.domain.name;
    if (!acc[d]) acc[d] = [];
    acc[d].push(s);
    return acc;
  }, {});

  const validated = data.skills.filter(s => s.is_validated).length;

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-[#28251d]">Compétences</h1>
          <p className="text-[#7a7974] mt-1 text-sm">Votre matrice de compétences personnelle.</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-[#01696f]">{validated}</p>
          <p className="text-xs text-[#7a7974]">validées / {data.skills.length}</p>
        </div>
      </div>

      {Object.keys(byDomain).length === 0 ? (
        <div className="text-center py-12">
          <p className="text-4xl mb-4">🎯</p>
          <h2 className="text-lg font-semibold text-[#28251d] mb-2">Aucune compétence assignée</h2>
          <p className="text-sm text-[#7a7974]">Vos compétences apparaîtront ici au fil de votre formation.</p>
        </div>
      ) : (
        Object.entries(byDomain).map(([domain, skills]) => (
          <div key={domain} className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-[#dcd9d5] bg-[#f3f0ec]">
              <h2 className="text-xs font-semibold text-[#7a7974] uppercase tracking-wide">{domain}</h2>
            </div>
            {skills.map(skill => (
              <SkillRow key={skill.skill.id} skill={skill} onRequest={requestValidation} />
            ))}
          </div>
        ))
      )}
    </div>
  );
}
