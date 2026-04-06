import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useParams, useNavigate } from 'react-router-dom';
import { evaluationsApi } from '../../api/evaluations';
import type { QuizResult } from '../../types';

export default function QuizPage() {
  const { quizId } = useParams<{ quizId: string }>();
  const navigate = useNavigate();
  const [answers, setAnswers] = useState<Record<string, string[]>>({});
  const [textAnswers, setTextAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [attemptId, setAttemptId] = useState<string | null>(null);

  const { data: quiz, isLoading } = useQuery({
    queryKey: ['quiz', quizId],
    queryFn: () => evaluationsApi.getQuiz(quizId!),
    enabled: !!quizId,
  });

  const { mutate: startQuiz, isPending: isStarting } = useMutation({
    mutationFn: () => evaluationsApi.startQuiz(quizId!),
    onSuccess: (data) => setAttemptId(data.attempt_id),
  });

  const { mutate: submit, isPending: isSubmitting } = useMutation({
    mutationFn: (payload: Parameters<typeof evaluationsApi.submitQuiz>[1]) =>
      evaluationsApi.submitQuiz(attemptId!, payload),
    onSuccess: (data) => setResult(data),
  });

  const handleToggleChoice = (questionId: string, choiceId: string, isMulti: boolean) => {
    setAnswers(prev => {
      const current = prev[questionId] ?? [];
      if (isMulti) {
        return {
          ...prev,
          [questionId]: current.includes(choiceId)
            ? current.filter(id => id !== choiceId)
            : [...current, choiceId],
        };
      }
      return { ...prev, [questionId]: [choiceId] };
    });
  };

  const handleStartQuiz = () => {
    startQuiz();
  };

  const handleSubmit = () => {
    if (!quiz) return;
    const payload = {
      answers: quiz.questions.map(q => ({
        question_id: q.id,
        ...(q.question_type === 'OPEN'
          ? { text_answer: textAnswers[q.id] ?? '' }
          : { choice_ids: answers[q.id] ?? [] }),
      })),
    };
    submit(payload);
  };

  if (isLoading) {
    return (
      <div className="p-8 space-y-4 max-w-2xl mx-auto">
        {[1, 2, 3].map(i => <div key={i} className="h-24 rounded-xl bg-[#f3f0ec] animate-pulse" />)}
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="p-8 text-center">
        <p className="text-[#a12c7b]">Quiz introuvable.</p>
        <button onClick={() => navigate(-1)} className="mt-3 text-sm text-[#01696f] underline">Retour</button>
      </div>
    );
  }

  // ── Écran de démarrage ──────────────────────────────────────
  if (!attemptId) {
    return (
      <div className="p-8 max-w-lg mx-auto space-y-6 mt-8">
        <div className="text-center">
          <p className="text-5xl mb-4">📝</p>
          <h1 className="text-2xl font-semibold text-[#28251d]">{quiz.title}</h1>
          <p className="text-[#7a7974] mt-3">{quiz.questions.length} questions · Seuil : {quiz.pass_threshold}%</p>
        </div>
        <button
          onClick={handleStartQuiz}
          disabled={isStarting}
          className="w-full bg-[#01696f] text-white py-3 rounded-xl font-medium hover:bg-[#0c4e54] transition-colors disabled:opacity-50"
        >
          {isStarting ? 'Démarrage...' : 'Commencer le quiz'}
        </button>
      </div>
    );
  }

  // ── Résultat ────────────────────────────────────────────────────
  if (result) {
    return (
      <div className="p-8 max-w-lg mx-auto text-center space-y-6 mt-8">
        <div className={`w-20 h-20 rounded-full flex items-center justify-center text-3xl mx-auto ${
          result.passed ? 'bg-[#d4dfcc] text-[#437a22]' : 'bg-[#e0ced7] text-[#a12c7b]'
        }`}>
          {result.passed ? '✓' : '✕'}
        </div>
        <div>
          <h1 className="text-2xl font-semibold text-[#28251d]">
            {result.passed ? 'Quiz réussi !' : 'Quiz non réussi'}
          </h1>
          <p className="text-[#7a7974] mt-2">
            Score : <span className="font-semibold text-[#28251d]">{result.score}%</span>
            {' '}— {result.correct_answers}/{result.total_questions} bonnes réponses
          </p>
        </div>
        {result.passed ? (
          <p className="text-sm text-[#437a22]">Seuil de réussite atteint ({quiz.pass_threshold}%). Félicitations !</p>
        ) : (
          <p className="text-sm text-[#a12c7b]">Seuil requis : {quiz.pass_threshold}%. Vous pouvez retenter.</p>
        )}
        <button onClick={() => navigate(-1)} className="text-sm border border-[#dcd9d5] px-4 py-2 rounded-lg hover:bg-[#f3f0ec] transition-colors w-full">
          Retour
        </button>
      </div>
    );
  }

  // ── Quiz ────────────────────────────────────────────────────────
  return (
    <div className="p-8 max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-[#28251d]">{quiz.title}</h1>
        <p className="text-[#7a7974] mt-1 text-sm">
          {quiz.questions.length} questions · Seuil de réussite : {quiz.pass_threshold}%
        </p>
      </div>

      {quiz.questions.map((q, idx) => (
        <div key={q.id} className="bg-[#f9f8f5] border border-[#dcd9d5] rounded-xl p-5 space-y-3">
          <p className="text-sm font-semibold text-[#28251d]">
            {idx + 1}. {q.text}
          </p>

          {q.question_type === 'OPEN' ? (
            <textarea
              rows={3}
              className="w-full text-sm border border-[#dcd9d5] rounded-lg px-3 py-2 bg-white focus:outline-none focus:border-[#01696f] resize-none"
              placeholder="Votre réponse..."
              value={textAnswers[q.id] ?? ''}
              onChange={e => setTextAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
            />
          ) : (
            <div className="space-y-2">
              {q.choices.map(choice => {
                const selected = (answers[q.id] ?? []).includes(choice.id);
                return (
                  <button
                    key={choice.id}
                    onClick={() => handleToggleChoice(q.id, choice.id, q.question_type === 'MCQ')}
                    className={`w-full text-left text-sm px-4 py-2.5 rounded-lg border transition-colors ${
                      selected
                        ? 'bg-[#cedcd8] border-[#01696f] text-[#0c4e54]'
                        : 'bg-white border-[#dcd9d5] text-[#28251d] hover:border-[#01696f]'
                    }`}
                  >
                    {choice.text}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      ))}

      <button
        onClick={handleSubmit}
        disabled={isSubmitting}
        className="w-full bg-[#01696f] text-white py-3 rounded-xl font-medium hover:bg-[#0c4e54] transition-colors disabled:opacity-50"
      >
        {isSubmitting ? 'Envoi...' : 'Soumettre le quiz'}
      </button>
    </div>
  );
}
