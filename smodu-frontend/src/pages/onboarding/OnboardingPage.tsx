import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { onboardingApi } from '../../api/onboarding';
import type { OnboardingStep } from '../../types';

const STEP_TYPE_LABELS: Record<string, string> = {
  document_read: '📄 Document',
  task_complete: '✅ Tâche',
  video_watch:   '🎬 Vidéo',
  form_fill:     '📝 Formulaire',
};

function StepCard({ step, onComplete }: { step: OnboardingStep; onComplete: (id: string) => void }) {
  return (
    <div className={`border rounded-xl p-5 transition-all ${
      step.is_completed
        ? 'bg-[#f3f0ec] border-[#dcd9d5] opacity-70'
        : 'bg-[#f9f8f5] border-[#dcd9d5] hover:border-[#01696f]'
    }`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-[#7a7974]">{STEP_TYPE_LABELS[step.step_type]}</span>
            {step.is_mandatory && (
              <span className="text-xs bg-[#fdd1a4] text-[#da7101] px-2 py-0.5 rounded-full">Obligatoire</span>
            )}
          </div>
          <h3 className="text-sm font-semibold text-[#28251d]">{step.title}</h3>
          {step.description && (
            <p className="text-xs text-[#7a7974] mt-1 leading-relaxed">{step.description}</p>
          )}
          {step.document_url && (
            <a
              href={step.document_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-2 text-xs text-[#01696f] underline hover:text-[#0c4e54]"
            >
              Ouvrir le document →
            </a>
          )}
        </div>
        <div className="shrink-0">
          {step.is_completed ? (
            <span className="text-[#437a22] text-lg">✓</span>
          ) : (
            <button
              onClick={() => onComplete(step.id)}
              className="text-xs bg-[#01696f] text-white px-3 py-1.5 rounded-lg hover:bg-[#0c4e54] transition-colors"
            >
              Marquer fait
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function OnboardingPage() {
  const qc = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ['onboarding', 'journey'],
    queryFn: onboardingApi.getMyJourney,
  });

  const { mutate: completeStep } = useMutation({
    mutationFn: onboardingApi.completeStep,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['onboarding', 'journey'] }),
  });

  if (isLoading) {
    return (
      <div className="p-8 space-y-3 max-w-2xl mx-auto">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-20 rounded-xl bg-[#f3f0ec] animate-pulse" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-8 text-center">
        <p className="text-[#a12c7b]">Impossible de charger le parcours d'onboarding.</p>
      </div>
    );
  }

  const pending = data.steps.filter(s => !s.is_completed);
  const done    = data.steps.filter(s => s.is_completed);

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-[#28251d]">{data.template_title}</h1>
        <p className="text-[#7a7974] mt-1">
          {data.completed_steps} / {data.total_steps} étapes complétées
        </p>
      </div>

      {/* Barre de progression */}
      <div>
        <div className="flex justify-between text-xs text-[#7a7974] mb-2">
          <span>Progression</span>
          <span className="font-semibold text-[#01696f]">{data.completion_percentage}%</span>
        </div>
        <div className="h-2 bg-[#e6e4df] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#01696f] rounded-full transition-all duration-700"
            style={{ width: `${data.completion_percentage}%` }}
          />
        </div>
      </div>

      {/* Étapes à faire */}
      {pending.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-xs font-semibold text-[#7a7974] uppercase tracking-wide">À compléter</h2>
          {pending.map(step => (
            <StepCard key={step.id} step={step} onComplete={completeStep} />
          ))}
        </div>
      )}

      {/* Étapes terminées */}
      {done.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-xs font-semibold text-[#7a7974] uppercase tracking-wide">Complétées</h2>
          {done.map(step => (
            <StepCard key={step.id} step={step} onComplete={completeStep} />
          ))}
        </div>
      )}

      {data.completion_percentage === 100 && (
        <div className="bg-[#d4dfcc] border border-[#437a22] rounded-xl p-5 text-center">
          <p className="text-[#437a22] font-semibold">🎉 Onboarding terminé ! Bravo !</p>
        </div>
      )}
    </div>
  );
}
