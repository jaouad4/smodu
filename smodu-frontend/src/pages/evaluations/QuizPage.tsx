import { ArrowLeftOutlined, ArrowRightOutlined, CheckCircleFilled, CloseCircleFilled } from '@ant-design/icons';
import { Alert, Button, Card, Checkbox, Progress, Radio, Result, Skeleton, Space, Typography } from 'antd';
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuiz, useSubmitQuiz } from '@/hooks/useEvaluations';
import type { SubmitAnswerPayload } from '@/types';

const { Title, Text } = Typography;

const QuizPage = () => {
  const { quizId } = useParams<{ quizId: string }>();
  const { data: quiz, isLoading } = useQuiz(Number(quizId));
  const { mutate: submit, isPending, data: result } = useSubmitQuiz(Number(quizId));

  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number[]>>({});

  if (isLoading) return <Skeleton active paragraph={{ rows: 8 }} />;
  if (!quiz) return null;

  // ─── Résultat final ────────────────────────────────────
  if (result) {
    const passed = (result as any).passed as boolean;
    return (
      <div style={{ maxWidth: 600, margin: '0 auto' }}>
        <Result
          icon={passed
            ? <CheckCircleFilled style={{ color: '#437a22' }} />
            : <CloseCircleFilled style={{ color: '#a12c7b' }} />
          }
          title={passed ? '🎉 Quiz réussi !' : 'Quiz non validé'}
          subTitle={`Score : ${(result as any).score}% — Seuil requis : ${quiz.pass_threshold}%`}
          status={passed ? 'success' : 'error'}
          extra={[
            <Button type="primary" key="back" onClick={() => history.back()}>
              Retour
            </Button>,
          ]}
        />
        {(result as any).feedback && (
          <Card title="Feedback détaillé" style={{ marginTop: 16 }}>
            {((result as any).feedback as { question: string; correct: boolean; explanation: string }[]).map((fb, i) => (
              <Alert
                key={i}
                type={fb.correct ? 'success' : 'error'}
                message={fb.question}
                description={fb.explanation}
                style={{ marginBottom: 8 }}
                showIcon
              />
            ))}
          </Card>
        )}
      </div>
    );
  }

  // ─── Quiz en cours ────────────────────────────────────
  const question = quiz.questions[currentIndex];
  const isLast = currentIndex === quiz.questions.length - 1;
  const selectedChoices = answers[question.id] ?? [];
  const progressPercent = Math.round(((currentIndex + 1) / quiz.questions.length) * 100);

  const handleChoiceChange = (choiceId: number, multi = false) => {
    if (multi) {
      setAnswers(prev => {
        const current = prev[question.id] ?? [];
        return {
          ...prev,
          [question.id]: current.includes(choiceId)
            ? current.filter(id => id !== choiceId)
            : [...current, choiceId],
        };
      });
    } else {
      setAnswers(prev => ({ ...prev, [question.id]: [choiceId] }));
    }
  };

  const handleSubmit = () => {
    const payload: SubmitAnswerPayload[] = Object.entries(answers).map(
      ([questionId, choiceIds]) => ({ question_id: Number(questionId), choice_ids: choiceIds })
    );
    submit(payload);
  };

  return (
    <div style={{ maxWidth: 680, margin: '0 auto' }}>
      <Title level={2}>{quiz.title}</Title>

      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <Text type="secondary">Question {currentIndex + 1} / {quiz.questions.length}</Text>
          <Text type="secondary">Seuil : {quiz.pass_threshold}%</Text>
        </div>
        <Progress percent={progressPercent} strokeColor="#01696f" showInfo={false} />
      </div>

      <Card>
        <Title level={4} style={{ marginBottom: 24 }}>{question.text}</Title>

        <Space direction="vertical" style={{ width: '100%' }}>
          {question.question_type === 'MCQ' ? (
            question.choices.map(choice => (
              <Card
                key={choice.id}
                size="small"
                hoverable
                style={{
                  borderColor: selectedChoices.includes(choice.id) ? '#01696f' : undefined,
                  background: selectedChoices.includes(choice.id) ? '#cedcd8' : undefined,
                  cursor: 'pointer',
                }}
                onClick={() => handleChoiceChange(choice.id, true)}
              >
                <Checkbox checked={selectedChoices.includes(choice.id)}>
                  {choice.text}
                </Checkbox>
              </Card>
            ))
          ) : (
            question.choices.map(choice => (
              <Card
                key={choice.id}
                size="small"
                hoverable
                style={{
                  borderColor: selectedChoices.includes(choice.id) ? '#01696f' : undefined,
                  background: selectedChoices.includes(choice.id) ? '#cedcd8' : undefined,
                  cursor: 'pointer',
                }}
                onClick={() => handleChoiceChange(choice.id)}
              >
                <Radio checked={selectedChoices.includes(choice.id)}>
                  {choice.text}
                </Radio>
              </Card>
            ))
          )}
        </Space>
      </Card>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 24 }}>
        <Button
          icon={<ArrowLeftOutlined />}
          disabled={currentIndex === 0}
          onClick={() => setCurrentIndex(i => i - 1)}
        >
          Précédent
        </Button>
        {isLast ? (
          <Button
            type="primary"
            loading={isPending}
            disabled={selectedChoices.length === 0}
            onClick={handleSubmit}
          >
            Soumettre le quiz
          </Button>
        ) : (
          <Button
            type="primary"
            icon={<ArrowRightOutlined />}
            iconPosition="end"
            disabled={selectedChoices.length === 0}
            onClick={() => setCurrentIndex(i => i + 1)}
          >
            Suivant
          </Button>
        )}
      </div>
    </div>
  );
};

export default QuizPage;
