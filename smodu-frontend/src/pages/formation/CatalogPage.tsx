import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { formationApi } from '../../api/formation';
import type { LearningPath } from '../../types';

const LEVEL_COLORS: Record<string, string> = {
  DISCOVERY:     '#006494',
  BEGINNER:      '#437a22',
  INTERMEDIATE:  '#da7101',
  AUTONOMOUS:    '#d19900',
  PROJECT_READY: '#01696f',
};

function PathCard({ path, onEnroll }: { path: LearningPath; onEnroll: (id: string) => void }) {
  const navigate = useNavigate();
  const firstModule = path.modules?.[0];

  return (
    <div className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl p-6 flex flex-col gap-4 hover:border-[#01696f] transition-colors">
      <div>
        <h3 className="text-base font-semibold text-[#28251d]">{path.title}</h3>
        <p className="text-sm text-[#7a7974] mt-1 line-clamp-2">{path.description}</p>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs text-[#7a7974]">{path.modules?.length ?? 0} modules</span>
        {firstModule && (
          <span
            className="text-xs px-2 py-0.5 rounded-full"
            style={{ background: `${LEVEL_COLORS[firstModule.level]}18`, color: LEVEL_COLORS[firstModule.level] }}
          >
            {firstModule.level}
          </span>
        )}
      </div>

      {path.is_enrolled && (
        <div>
          <div className="flex justify-between text-xs text-[#7a7974] mb-1">
            <span>Progression</span>
            <span className="text-[#01696f] font-medium">{path.completion_percentage}%</span>
          </div>
          <div className="h-1.5 bg-[#e6e4df] rounded-full">
            <div className="h-full bg-[#01696f] rounded-full" style={{ width: `${path.completion_percentage}%` }} />
          </div>
        </div>
      )}

      <div className="mt-auto">
        {path.is_enrolled ? (
          <button
            onClick={() => firstModule && navigate(`/formation/modules/${firstModule.id}`)}
            className="w-full text-sm bg-[#01696f] text-white px-4 py-2 rounded-lg hover:bg-[#0c4e54] transition-colors"
          >
            Continuer →
          </button>
        ) : (
          <button
            onClick={() => onEnroll(path.id)}
            className="w-full text-sm border border-[#01696f] text-[#01696f] px-4 py-2 rounded-lg hover:bg-[#cedcd8] transition-colors"
          >
            S'inscrire
          </button>
        )}
      </div>
    </div>
  );
}

export default function CatalogPage() {
  const qc = useQueryClient();

  const { data: catalog, isLoading } = useQuery({
    queryKey: ['formation', 'catalog'],
    queryFn: formationApi.getCatalog,
  });

  const { mutate: enroll } = useMutation({
    mutationFn: formationApi.enroll,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['formation', 'catalog'] }),
  });

  if (isLoading) {
    return (
      <div className="p-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-56 rounded-xl bg-[#f3f0ec] animate-pulse" />
        ))}
      </div>
    );
  }

  if (!catalog || catalog.length === 0) {
    return (
      <div className="p-8 flex flex-col items-center justify-center min-h-[50vh] text-center">
        <p className="text-4xl mb-4">📚</p>
        <h2 className="text-lg font-semibold text-[#28251d] mb-2">Aucun parcours disponible</h2>
        <p className="text-sm text-[#7a7974]">Les parcours de formation apparaîtront ici.</p>
      </div>
    );
  }

  const enrolled = catalog.filter(p => p.is_enrolled);
  const available = catalog.filter(p => !p.is_enrolled);

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10">
      <div>
        <h1 className="text-2xl font-semibold text-[#28251d]">Formation</h1>
        <p className="text-[#7a7974] mt-1">Vos parcours d'apprentissage.</p>
      </div>

      {enrolled.length > 0 && (
        <div>
          <h2 className="text-xs font-semibold text-[#7a7974] uppercase tracking-wide mb-4">En cours</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {enrolled.map(p => <PathCard key={p.id} path={p} onEnroll={enroll} />)}
          </div>
        </div>
      )}

      {available.length > 0 && (
        <div>
          <h2 className="text-xs font-semibold text-[#7a7974] uppercase tracking-wide mb-4">Disponibles</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {available.map(p => <PathCard key={p.id} path={p} onEnroll={enroll} />)}
          </div>
        </div>
      )}
    </div>
  );
}
