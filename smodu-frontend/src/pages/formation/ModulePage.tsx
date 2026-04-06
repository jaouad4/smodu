import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { formationApi } from '../../api/formation';
import type { Lesson } from '../../types';

const LESSON_ICONS: Record<string, string> = {
  video: '🎬', pdf: '📄', text: '📖', exercise: '✏️',
};

function LessonRow({ lesson, onComplete }: { lesson: Lesson; onComplete: (id: number) => void }) {
  return (
    <div className={`flex items-center gap-4 px-4 py-3 rounded-lg border transition-colors ${
      lesson.is_completed
        ? 'bg-[#f3f0ec] border-[#dcd9d5]'
        : 'bg-[#f9f8f5] border-[#dcd9d5] hover:border-[#01696f]'
    }`}>
      <span className="text-lg shrink-0">{LESSON_ICONS[lesson.lesson_type] ?? '📌'}</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-[#28251d] truncate">{lesson.title}</p>
        <p className="text-xs text-[#7a7974]">{lesson.duration_minutes} min</p>
      </div>
      {lesson.content_url && (
        <a
          href={lesson.content_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-[#01696f] underline hover:text-[#0c4e54] shrink-0"
        >
          Ouvrir
        </a>
      )}
      {lesson.is_completed ? (
        <span className="text-[#437a22] shrink-0">✓</span>
      ) : (
        <button
          onClick={() => onComplete(lesson.id)}
          className="shrink-0 text-xs bg-[#01696f] text-white px-3 py-1 rounded-lg hover:bg-[#0c4e54] transition-colors"
        >
          Terminer
        </button>
      )}
    </div>
  );
}

export default function ModulePage() {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: module, isLoading, isError } = useQuery({
    queryKey: ['formation', 'module', moduleId],
    queryFn: () => formationApi.getModule(Number(moduleId)),
    enabled: !!moduleId,
  });

  const { mutate: completeLesson } = useMutation({
    mutationFn: formationApi.completeLesson,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['formation', 'module', moduleId] }),
  });

  if (isLoading) {
    return (
      <div className="p-8 space-y-3 max-w-2xl mx-auto">
        <div className="h-8 w-48 rounded bg-[#f3f0ec] animate-pulse" />
        {[1, 2, 3].map(i => <div key={i} className="h-14 rounded-lg bg-[#f3f0ec] animate-pulse" />)}
      </div>
    );
  }

  if (isError || !module) {
    return (
      <div className="p-8 text-center">
        <p className="text-[#a12c7b]">Module introuvable.</p>
        <button onClick={() => navigate('/formation')} className="mt-3 text-sm text-[#01696f] underline">
          Retour au catalogue
        </button>
      </div>
    );
  }

  if (module.is_locked) {
    return (
      <div className="p-8 max-w-2xl mx-auto text-center space-y-4">
        <p className="text-4xl">🔒</p>
        <h2 className="text-lg font-semibold text-[#28251d]">Module verrouillé</h2>
        <p className="text-sm text-[#7a7974]">Complétez les modules précédents pour déverrouiller celui-ci.</p>
        <button onClick={() => navigate('/formation')} className="text-sm text-[#01696f] underline">
          Retour au catalogue
        </button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-6">
      <button
        onClick={() => navigate('/formation')}
        className="text-xs text-[#7a7974] hover:text-[#28251d] transition-colors"
      >
        ← Retour au catalogue
      </button>

      <div>
        <h1 className="text-2xl font-semibold text-[#28251d]">{module.title}</h1>
        <p className="text-[#7a7974] mt-1 text-sm">{module.description}</p>
      </div>

      {/* Progression */}
      <div>
        <div className="flex justify-between text-xs text-[#7a7974] mb-2">
          <span>Progression du module</span>
          <span className="text-[#01696f] font-medium">{module.completion_percentage}%</span>
        </div>
        <div className="h-2 bg-[#e6e4df] rounded-full">
          <div className="h-full bg-[#01696f] rounded-full transition-all" style={{ width: `${module.completion_percentage}%` }} />
        </div>
      </div>

      {/* Leçons */}
      <div className="space-y-2">
        <h2 className="text-xs font-semibold text-[#7a7974] uppercase tracking-wide">
          Leçons ({module.lessons.length})
        </h2>
        {module.lessons.length === 0 ? (
          <p className="text-sm text-[#7a7974] text-center py-6">Aucune leçon disponible.</p>
        ) : (
          module.lessons
            .sort((a, b) => a.order - b.order)
            .map(lesson => (
              <LessonRow key={lesson.id} lesson={lesson} onComplete={completeLesson} />
            ))
        )}
      </div>

      {module.completion_percentage === 100 && (
        <div className="bg-[#d4dfcc] border border-[#437a22] rounded-xl p-4 text-center">
          <p className="text-[#437a22] font-semibold">✓ Module complété !</p>
        </div>
      )}
    </div>
  );
}
