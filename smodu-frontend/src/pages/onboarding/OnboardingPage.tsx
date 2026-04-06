import { CheckCircleOutlined, ClockCircleOutlined, FilePdfOutlined, PlayCircleOutlined, FormOutlined, CheckSquareOutlined } from '@ant-design/icons';
import { Badge, Button, Card, Progress, Skeleton, Steps, Tag, Timeline, Typography, message } from 'antd';
import type { StepType } from '@/types';
import { useCompleteStep, useMyJourney } from '@/hooks/useOnboarding';

const { Title, Text } = Typography;

const stepTypeIcon: Record<StepType, React.ReactNode> = {
  document_read: <FilePdfOutlined />,
  video_watch: <PlayCircleOutlined />,
  task_complete: <CheckSquareOutlined />,
  form_fill: <FormOutlined />,
};

const stepTypeLabel: Record<StepType, string> = {
  document_read: 'Document',
  video_watch: 'Vidéo',
  task_complete: 'Tâche',
  form_fill: 'Formulaire',
};

const OnboardingPage = () => {
  const { data: journey, isLoading } = useMyJourney();
  const { mutate: completeStep, isPending } = useCompleteStep();

  const handleComplete = (stepId: number) => {
    completeStep(stepId, {
      onSuccess: () => message.success('Étape validée !'),
      onError: () => message.error('Erreur lors de la validation.'),
    } as any);
  };

  if (isLoading) return <Skeleton active paragraph={{ rows: 8 }} />;
  if (!journey) return null;

  const currentStep = journey.steps.findIndex(s => !s.is_completed);

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Title level={2}>Mon Parcours d'Onboarding</Title>
      <Text type="secondary">{journey.template_title}</Text>

      <Card style={{ marginTop: 24, marginBottom: 32 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
          <Text strong>Progression globale</Text>
          <Text type="secondary">{journey.completed_steps} / {journey.total_steps} étapes</Text>
        </div>
        <Progress
          percent={journey.completion_percentage}
          strokeColor="#01696f"
          size="default"
        />
      </Card>

      <Steps
        direction="vertical"
        current={currentStep === -1 ? journey.total_steps : currentStep}
        items={journey.steps.map((step) => ({
          title: (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span>{step.title}</span>
              {step.is_mandatory && <Tag color="red" style={{ fontSize: 11 }}>Obligatoire</Tag>}
              <Tag icon={stepTypeIcon[step.step_type]} color="default" style={{ fontSize: 11 }}>
                {stepTypeLabel[step.step_type]}
              </Tag>
            </div>
          ),
          description: (
            <div style={{ paddingTop: 8 }}>
              <Text type="secondary">{step.description}</Text>
              {step.document_url && (
                <div style={{ marginTop: 8 }}>
                  <Button
                    size="small"
                    icon={<FilePdfOutlined />}
                    href={step.document_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Télécharger le document
                  </Button>
                </div>
              )}
              {!step.is_completed && (
                <Button
                  type="primary"
                  size="small"
                  style={{ marginTop: 8 }}
                  loading={isPending}
                  onClick={() => handleComplete(step.id)}
                >
                  Marquer comme terminé
                </Button>
              )}
            </div>
          ),
          icon: step.is_completed
            ? <CheckCircleOutlined style={{ color: '#01696f' }} />
            : <ClockCircleOutlined style={{ color: '#7a7974' }} />,
          status: step.is_completed ? 'finish' : 'wait',
        }))}
      />
    </div>
  );
};

export default OnboardingPage;
