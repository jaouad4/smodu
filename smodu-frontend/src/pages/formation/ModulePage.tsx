import { ArrowLeftOutlined, CheckCircleOutlined, ClockCircleOutlined, FilePdfOutlined, PlayCircleOutlined, ReadOutlined, ToolOutlined } from '@ant-design/icons';
import { Button, Card, Divider, List, Progress, Skeleton, Tag, Typography, message } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { useCompleteLesson, useModule } from '@/hooks/useFormation';
import type { LessonType } from '@/types';

const { Title, Text } = Typography;

const lessonTypeIcon: Record<LessonType, React.ReactNode> = {
  video: <PlayCircleOutlined />,
  pdf: <FilePdfOutlined />,
  text: <ReadOutlined />,
  exercise: <ToolOutlined />,
};

const lessonTypeLabel: Record<LessonType, string> = {
  video: 'Vidéo',
  pdf: 'PDF',
  text: 'Lecture',
  exercise: 'Exercice',
};

const ModulePage = () => {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();
  const { data: module, isLoading } = useModule(Number(moduleId));
  const { mutate: completeLesson, isPending } = useCompleteLesson();

  const handleComplete = (lessonId: number) => {
    completeLesson(lessonId, {
      onSuccess: () => message.success('Leçon complétée !'),
      onError: () => message.error('Erreur lors de la complétion.'),
    } as any);
  };

  if (isLoading) return <Skeleton active paragraph={{ rows: 10 }} />;
  if (!module) return null;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Button
        icon={<ArrowLeftOutlined />}
        type="link"
        style={{ paddingLeft: 0, marginBottom: 16 }}
        onClick={() => navigate('/formation')}
      >
        Retour au catalogue
      </Button>

      <Title level={2}>{module.title}</Title>
      <Text type="secondary">{module.description}</Text>

      <Card style={{ marginTop: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
          <Text strong>Progression du module</Text>
          <Text type="secondary">{module.completion_percentage}%</Text>
        </div>
        <Progress percent={module.completion_percentage} strokeColor="#01696f" />
      </Card>

      <Divider orientation="left">Leçons</Divider>

      <List
        dataSource={module.lessons}
        renderItem={(lesson) => (
          <List.Item
            key={lesson.id}
            actions={[
              !lesson.is_completed && (
                <Button
                  key="complete"
                  size="small"
                  type="primary"
                  loading={isPending}
                  onClick={() => handleComplete(lesson.id)}
                >
                  Terminer
                </Button>
              ),
            ].filter(Boolean)}
          >
            <List.Item.Meta
              avatar={
                lesson.is_completed
                  ? <CheckCircleOutlined style={{ fontSize: 20, color: '#01696f' }} />
                  : <ClockCircleOutlined style={{ fontSize: 20, color: '#7a7974' }} />
              }
              title={
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span>{lesson.title}</span>
                  <Tag icon={lessonTypeIcon[lesson.lesson_type]} color="default" style={{ fontSize: 11 }}>
                    {lessonTypeLabel[lesson.lesson_type]}
                  </Tag>
                </div>
              }
              description={
                <Text type="secondary" style={{ fontSize: 12 }}>
                  ⏱ {lesson.duration_minutes} min
                </Text>
              }
            />
          </List.Item>
        )}
      />
    </div>
  );
};

export default ModulePage;
